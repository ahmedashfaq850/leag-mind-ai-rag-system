from pydantic import BaseModel, Field

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

from backend.core.config import get_settings
from backend.core.logging import get_logger
from backend.generation.prompts import SYSTEM_PROMPT

logger = get_logger(__name__)


class RAGOutput(BaseModel):
    """Structured output: answer + only the documents actually used."""

    answer: str = Field(description="The answer to the question based on the context.")
    sources_used: list[str] = Field(
        description="Document file names (e.g. 'document 3.pdf') that were actually used to answer. Only include docs you cited.",
        default_factory=list,
    )


def format_context(chunks: list[dict]) -> str:
    parts = []
    for c in chunks:
        doc_name = c.get("metadata", {}).get("file_name", "unknown_file")
        parts.append(f"[File: {doc_name}]\n{c.get('text', '')}")
    return "\n\n".join(parts)


def build_rag_chain():
    s = get_settings()
    llm = ChatOpenAI(
        model=s.LLM_MODEL,
        temperature=s.LLM_TEMPERATURE,
        api_key=s.OPENAI_API_KEY,
    ).with_structured_output(RAGOutput)

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "Context:\n{context}\n\nQuestion: {question}\n\nProvide your answer and list ONLY the file names you actually used in sources_used."),
    ])

    chain = (
        RunnablePassthrough.assign(context=lambda x: format_context(x["chunks"]))
        | prompt
        | llm
    )

    logger.info("[generation.chain] RAG chain built (structured output)")
    return chain