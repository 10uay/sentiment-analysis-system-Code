from app.services.rag_service import RAGService


def test_rag_default_context():
    service = RAGService()
    ctx = service.retrieve("النظام رائع", "ar")
    assert isinstance(ctx, list)
