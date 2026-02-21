from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from backend.core.config import get_settings
from backend.core.logging import setup_logging, get_logger

from backend.api.schemas import QueryRequest, QueryResponse
from backend.api.deps import get_assets, get_reranker, get_cache, get_chain
from backend.retrieval.retriever import build_merged_chunks

logger = get_logger(__name__)

def create_app() -> FastAPI:
    s = get_settings()
    setup_logging(s.LOG_LEVEL)

    app = FastAPI(title="LegalMind API", version="1.0.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.post("/query", response_model=QueryResponse)
    def query_endpoint(
        request: QueryRequest,
        assets=Depends(get_assets),
        reranker=Depends(get_reranker),
        cache=Depends(get_cache),
        chain=Depends(get_chain),
    ):
        logger.info(f"[api] question={request.question}")

        # 1) cache
        cached = cache.check(request.question)
        if cached:
            return QueryResponse(answer=cached, sources=[], cache_hit=True)

        # 2) hybrid retrieval
        merged_chunks = build_merged_chunks(assets, request.question, top_k=20)

        # optional metadata filter (doc_type)
        if request.doc_type:
            merged_chunks = [
                c for c in merged_chunks
                if c.get("metadata", {}).get("doc_type") == request.doc_type
            ]

        # 3) rerank
        top_chunks = reranker.rerank(request.question, merged_chunks, top_n=5)

        # 4) generate (structured: answer + sources_used from LLM)
        output = chain.invoke({"question": request.question, "chunks": top_chunks})

        # 5) use LLM-cited sources only; validate against actual chunk file names
        valid_files = {c.get("metadata", {}).get("file_name") for c in top_chunks if c.get("metadata", {}).get("file_name")}
        sources = sorted(set(s for s in (output.sources_used or []) if s in valid_files))
        cache.save(request.question, output.answer)

        debug_payload = None
        if request.debug:
            debug_payload = {
                "retrieved_chunks": [
                    {
                        "id": c.get("id"),
                        "doc": c.get("metadata", {}).get("file_name"),
                        "text": c.get("text", "")[:2000]
                    }
                    for c in top_chunks
                ]
            }

        return QueryResponse(answer=output.answer, sources=sources, cache_hit=False, debug=debug_payload)

    return app

app = create_app()