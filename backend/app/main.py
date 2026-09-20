from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse
from app.config import get_settings
from app.db.database import Base, engine
from app.db import models as db_models  # noqa: F401
from app.api.routes import analyze, history, reports, models, auth


settings = get_settings()

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Arabic/English Sentiment Analysis System using modern language models.",
    docs_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=settings.api_prefix, tags=["Auth"])
app.include_router(analyze.router, prefix=settings.api_prefix, tags=["Analyze"])
app.include_router(history.router, prefix=settings.api_prefix, tags=["History"])
app.include_router(reports.router, prefix=settings.api_prefix, tags=["Reports"])
app.include_router(models.router, prefix=settings.api_prefix, tags=["Models"])


@app.get("/")
def root():
    return {
        "message": "Sentiment Analysis System API",
        "docs": "/docs",
        "api_prefix": settings.api_prefix,
    }


@app.get("/health")
def health():
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Custom themed Swagger UI (glassmorphism, matches the frontend)
# ---------------------------------------------------------------------------

SWAGGER_CSS = """
:root {
  --bg-1: #0b1437;
  --bg-2: #1a1145;
  --glass: rgba(255,255,255,0.06);
  --glass-border: rgba(255,255,255,0.12);
  --text: #e8edf7;
  --text-soft: #aab4cf;
  --accent: #6366f1;
  --accent-2: #8b5cf6;
}
body { background: radial-gradient(1200px 800px at 12% -8%, rgba(99,102,241,0.28), transparent 60%),
  radial-gradient(1000px 700px at 100% 0%, rgba(139,92,246,0.22), transparent 55%),
  radial-gradient(900px 700px at 85% 110%, rgba(59,130,246,0.22), transparent 55%),
  linear-gradient(160deg, var(--bg-1), var(--bg-2) 45%, #0e2a4a);
  background-attachment: fixed;
  font-family: 'Cairo', system-ui, -apple-system, 'Segoe UI', sans-serif;
}
.swagger-ui, .swagger-ui .opblock .opblock-section-header h4,
.swagger-ui .info .title, .swagger-ui .info li, .swagger-ui .info p,
.swagger-ui table thead tr td, .swagger-ui table thead tr th,
.swagger-ui .parameter__name, .swagger-ui .parameter__type,
.swagger-ui .response-col_status, .swagger-ui .response-col_description,
.swagger-ui .scheme-container .schemes > label,
.swagger-ui .models-control span, .swagger-ui .models h4,
.swagger-ui label, .swagger-ui select, .swagger-ui .btn,
.swagger-ui .dialog-ux .modal-ux-header h3,
.swagger-ui .dialog-ux .modal-ux-content h4,
.swagger-ui .dialog-ux .modal-ux-content p,
.swagger-ui section.models h4 span { color: var(--text) !important; }
.swagger-ui .topbar { display: none; }
.swagger-ui .info { margin: 40px 0 20px; }
.swagger-ui .info .title { color: #fff !important; font-weight: 800; }
.swagger-ui .info .base-url { color: var(--text-soft) !important; }
.swagger-ui .scheme-container {
  background: var(--glass); backdrop-filter: blur(14px);
  border: 1px solid var(--glass-border); border-radius: 16px; margin: 16px 0; padding: 16px 20px;
}
.swagger-ui .opblock {
  background: var(--glass) !important; backdrop-filter: blur(12px);
  border: 1px solid var(--glass-border) !important; border-radius: 14px !important;
  box-shadow: 0 12px 30px rgba(2,6,23,0.35) !important; margin: 0 0 16px !important;
}
.swagger-ui .opblock .opblock-summary { border: 0 !important; }
.swagger-ui .opblock-summary-path { color: #fff !important; }
.swagger-ui .opblock-summary-path a { color: #fff !important; }
.swagger-ui .opblock-summary-description { color: var(--text-soft) !important; }
.swagger-ui .opblock-summary-path-description-wrapper { color: var(--text) !important; }
.swagger-ui .opblock-tag { color: #fff !important; font-weight: 700; }
.swagger-ui .opblock .opblock-summary-method {
  border: 0 !important; box-shadow: 0 6px 16px rgba(99,102,241,0.4) !important;
}
.swagger-ui .opblock.opblock-post .opblock-summary-method { background: linear-gradient(135deg,#22c55e,#10b981) !important; }
.swagger-ui .opblock.opblock-get .opblock-summary-method { background: linear-gradient(135deg,#3b82f6,#6366f1) !important; }
.swagger-ui .opblock.opblock-delete .opblock-summary-method { background: linear-gradient(135deg,#ef4444,#dc2626) !important; }
.swagger-ui .opblock.opblock-put .opblock-summary-method { background: linear-gradient(135deg,#eab308,#f59e0b) !important; }
.swagger-ui .opblock-header { background: rgba(255,255,255,0.04) !important; }
.swagger-ui .opblock-body pre { background: rgba(0,0,0,0.3) !important; border-radius: 10px; }
.swagger-ui .opblock .opblock-section-header {
  background: rgba(255,255,255,0.04) !important;
  border-bottom: 1px solid var(--glass-border) !important;
}
.swagger-ui .opblock .opblock-section-header h4 { color: var(--text) !important; }
.swagger-ui .opblock-section-header__arrow { fill: var(--text-soft) !important; }
.swagger-ui .opblock-section-header__arrow.opened { fill: #a5b4fc !important; }
.swagger-ui table.parameters { background: transparent !important; }
.swagger-ui table.parameters thead tr td, .swagger-ui table.parameters thead tr th {
  background: rgba(255,255,255,0.05) !important; color: var(--text) !important;
  border-bottom: 1px solid var(--glass-border) !important;
}
.swagger-ui .parameters-col_name { color: var(--text) !important; }
.swagger-ui .parameters-col_description { color: var(--text-soft) !important; }
.swagger-ui .parameters-col_description p { color: var(--text-soft) !important; }
.swagger-ui .parameter__in, .swagger-ui .parameter__type { color: var(--text-muted) !important; }
.swagger-ui .parameter__deprecated { color: #fca5a5 !important; }
.swagger-ui .parameter__enum, .swagger-ui .parameter__default-value,
.swagger-ui .parameter__example { color: #c7d2fe !important; }
.swagger-ui .parameter__name { color: var(--text) !important; }
.swagger-ui .parameter__name.required { color: #fff !important; }
.swagger-ui .parameter__name.required::after { color: #fca5a5 !important; }
.swagger-ui .parameter__name.required::after { content: ' *'; }
.swagger-ui .table-container .parameters-col_description input[type=text] { color: var(--text) !important; }
.swagger-ui .btn.authorize, .swagger-ui .btn {
  background: var(--glass) !important; border: 1px solid var(--glass-border) !important;
  color: var(--text) !important; box-shadow: none !important;
}
.swagger-ui .btn.authorize { color: #a5b4fc !important; border-color: rgba(99,102,241,0.5) !important; }
.swagger-ui .btn.execute {
  background: linear-gradient(135deg, var(--accent), var(--accent-2)) !important;
  color: #fff !important; border: 0 !important; font-weight: 700;
}
.swagger-ui input[type=text], .swagger-ui input[type=password], .swagger-ui textarea, .swagger-ui select {
  background: rgba(255,255,255,0.05) !important; border: 1px solid var(--glass-border) !important;
  color: var(--text) !important; border-radius: 8px !important;
}
.swagger-ui select option { background: #16213e !important; color: var(--text) !important; }
.swagger-ui select {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' fill='none' stroke='%23aab4cf' stroke-width='2' viewBox='0 0 24 24'%3E%3Cpath d='m6 9 6 6 6-6'/%3E%3C/svg%3E") !important;
  background-repeat: no-repeat !important;
  background-position: left 10px center !important;
  padding-left: 34px !important;
  appearance: none !important;
  -webkit-appearance: none !important;
  -moz-appearance: none !important;
}
.swagger-ui input[type=text], .swagger-ui input[type=password], .swagger-ui textarea {
  color: var(--text) !important;
}
.swagger-ui input[type=text]::placeholder, .swagger-ui textarea::placeholder { color: var(--text-muted) !important; }
.swagger-ui .model-box, .swagger-ui section.models {
  background: var(--glass) !important; border: 1px solid var(--glass-border) !important;
  border-radius: 14px !important;
}
.swagger-ui .model { color: var(--text-soft) !important; }
.swagger-ui .model-toggle:after { background: var(--text-soft) !important; }
.swagger-ui .prop-type { color: #a5b4fc !important; }
.swagger-ui .prop-format { color: var(--text-soft) !important; }
.swagger-ui .parameter__name.required:after { color: #fca5a5 !important; }
.swagger-ui table thead tr td, .swagger-ui table thead tr th {
  background: rgba(255,255,255,0.05) !important; border-bottom: 1px solid var(--glass-border) !important;
}
.swagger-ui table tbody tr td { border-bottom: 1px solid rgba(255,255,255,0.06) !important; color: var(--text-soft) !important; }
.swagger-ui .response-control-media-type select { color: var(--text) !important; }
.swagger-ui .wrapper { padding: 0 28px; }
.swagger-ui .dialog-ux { background: rgba(2,6,23,0.7) !important; backdrop-filter: blur(6px); }
.swagger-ui .dialog-ux .modal-ux {
  background: #16213e !important; border: 1px solid var(--glass-border) !important;
  border-radius: 16px !important;
}
.swagger-ui .dialog-ux .modal-ux-header { background: rgba(255,255,255,0.05) !important; border-bottom: 1px solid var(--glass-border) !important; }
.swagger-ui .dialog-ux .modal-ux-header button.btn { color: var(--text-soft) !important; }
.swagger-ui .markdown pre, .swagger-ui .renderedMarkdown pre {
  background: rgba(0,0,0,0.3) !important; color: #e8edf7 !important; border-radius: 10px;
}
.swagger-ui .markdown code, .swagger-ui .renderedMarkdown code {
  background: rgba(255,255,255,0.08) !important; color: #c7d2fe !important; border-radius: 6px; padding: 2px 6px;
}
.swagger-ui .info a { color: #a5b4fc !important; }
.swagger-ui .download-contents { background: var(--glass) !important; color: var(--text) !important; border: 1px solid var(--glass-border) !important; }
"""


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    html = get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title="نظام تحليل المشاعر · API Docs",
        swagger_favicon_url="",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
        swagger_ui_parameters={
            "defaultModelsExpandDepth": 1,
            "docExpansion": "list",
            "filter": True,
            "displayRequestDuration": True,
            "deepLinking": True,
            "syntaxHighlight.theme": "arta",
        },
    ).body.decode()
    head_inject = (
        '<link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap" rel="stylesheet">'
        + "<style>" + SWAGGER_CSS + "</style>"
    )
    return HTMLResponse(content=html.replace("</head>", head_inject + "</head>"), media_type="text/html")
