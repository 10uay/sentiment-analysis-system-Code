from datetime import datetime, timezone
import json

from fastapi import APIRouter, Depends, Request, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.api.schemas import AnalyzeRequest, AnalyzeResponse, BatchAnalyzeRequest, BatchAnalyzeResponse
from app.dependencies import get_current_user, get_db, rate_limit
from app.db import crud
from app.db.database import SessionLocal
from app.services.cache_service import CacheService
from app.services.model_orchestrator import ModelOrchestrator
from app.services.preprocessor import TextPreprocessor
from app.services.rag_service import RAGService
from app.services.report_service import ReportService

router = APIRouter()

preprocessor = TextPreprocessor()
orchestrator = ModelOrchestrator()
rag_service = RAGService()
report_service = ReportService()
cache = CacheService()


def run_analysis(payload: AnalyzeRequest, db: Session, user: str) -> AnalyzeResponse:
    cache_key = cache.make_key("analyze", payload.model_name, payload.use_rag, payload.text)
    cached = cache.get_json(cache_key)
    if cached:
        return AnalyzeResponse(**cached)

    # 1) Text preprocessing
    clean = preprocessor.clean(payload.text)
    language = preprocessor.detect_language(clean)

    # 2) First prediction without RAG.
    # We do this first because we need the final label
    # in order to retrieve RAG examples with the same sentiment.
    initial_model_results = orchestrator.predict(
        text=clean,
        language=language,
        model_name=payload.model_name,
        context=[],
    )

    initial_final = orchestrator.aggregate(initial_model_results)

    # 3) Retrieve RAG context filtered by the predicted final label.
    # Example:
    # if final label = positive, retrieve positive examples only.
    # if final label = negative, retrieve negative examples only.
    # if final label = neutral, retrieve neutral examples only.
    rag_context = (
        rag_service.retrieve(
            clean,
            language=language,
            top_k=3,
            target_label=initial_final["label"],
        )
        if payload.use_rag
        else []
    )

    # 4) Keep the model result from the real model.
    # RAG is used here mainly for explanation/report context,
    # not for changing the trained model prediction.
    model_results = initial_model_results
    final = initial_final

    # 5) Generate report summary using filtered RAG context
    summary = report_service.generate_summary(
        text=payload.text,
        label=final["label"],
        confidence=final["confidence"],
        language=language,
        model_results=model_results,
        context=rag_context,
    )

    analysis_id = None

    # 6) Save analysis history if requested
    if payload.save_history:
        record = crud.create_analysis(
            db=db,
            user_id=user,
            text=payload.text,
            cleaned_text=clean,
            language=language,
            label=final["label"],
            confidence=final["confidence"],
            model_name=payload.model_name,
            raw_result={
                "model_results": [m.model_dump() for m in model_results],
                "rag_context": rag_context,
                "summary": summary,
            },
        )
        analysis_id = record.id

    response = AnalyzeResponse(
        id=analysis_id,
        original_text=payload.text,
        cleaned_text=clean,
        language=language,
        final_label=final["label"],
        confidence=final["confidence"],
        model_results=model_results,
        rag_context=rag_context,
        report_summary=summary,
        created_at=datetime.now(timezone.utc),
    )

    cache.set_json(cache_key, response.model_dump(mode="json"), ttl_seconds=300)
    return response


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_text(
    payload: AnalyzeRequest,
    request: Request,
    db: Session = Depends(get_db),
    user: str = Depends(get_current_user),
    _: bool = Depends(rate_limit),
):
    return run_analysis(payload, db, user)


@router.post("/analyze/batch", response_model=BatchAnalyzeResponse)
def batch_analyze(
    payload: BatchAnalyzeRequest,
    request: Request,
    db: Session = Depends(get_db),
    user: str = Depends(get_current_user),
    _: bool = Depends(rate_limit),
):
    results = []

    for text in payload.texts:
        result = run_analysis(
            AnalyzeRequest(
                text=text,
                model_name=payload.model_name,
                use_rag=payload.use_rag,
                save_history=payload.save_history,
            ),
            db=db,
            user=user,
        )
        results.append(result)

    counts = {}
    for item in results:
        counts[item.final_label] = counts.get(item.final_label, 0) + 1

    return BatchAnalyzeResponse(
        results=results,
        stats={
            "total": len(results),
            "label_counts": counts,
            "avg_confidence": sum(x.confidence for x in results) / max(len(results), 1),
        },
    )

@router.websocket("/ws/analyze")
async def analyze_websocket(websocket: WebSocket):
    await websocket.accept()
    db = SessionLocal()

    try:
        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)

            payload = AnalyzeRequest(
                text=data.get("text", ""),
                model_name=data.get("model_name", "ensemble"),
                use_rag=bool(data.get("use_rag", True)),
                save_history=bool(data.get("save_history", False)),
            )

            result = run_analysis(payload, db, "websocket")
            await websocket.send_json(result.model_dump(mode="json"))

    except WebSocketDisconnect:
        pass

    finally:
        db.close()