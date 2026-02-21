from pydantic import BaseModel
from typing import Optional, Any

class QueryRequest(BaseModel):
    question: str
    doc_type: str | None = None
    debug: bool = False   

class QueryResponse(BaseModel):
    answer: str
    sources: list[str]
    cache_hit: bool = False
    debug: Optional[dict[str, Any]] = None 