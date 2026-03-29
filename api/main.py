import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from src.rag.chain import query_rag

load_dotenv()

app = FastAPI(
    title       = "ERP LLM Intelligence API",
    description = "Natural language querying of SAP-structured ERP data using RAG",
    version     = "1.0.0"
)


class QueryRequest(BaseModel):
    question: str


class SourceRecord(BaseModel):
    record_id: str
    table:     str
    relevance: float
    text:      str


class QueryResponse(BaseModel):
    question: str
    answer:   str
    sources:  list


@app.get("/health")
def health():
    return {"status": "ok", "version": "1.0.0"}


@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    try:
        result = query_rag(req.question)
        return QueryResponse(
            question = result["question"],
            answer   = result["answer"],
            sources  = result["sources"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))