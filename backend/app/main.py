from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from app.utils import multiply_helper
from app.models import MultiplyRequest, MultiplyResponse

# Trivial refactor: add a comment for demo purposes
app = FastAPI()

@app.post("/multiply", response_model=MultiplyResponse)
def multiply_endpoint(req: MultiplyRequest):
    # Inefficient loop for demo (suggestion opportunity)
    result = 0
    for _ in range(req.b):
        for _ in range(req.a):
            result += 1
    return MultiplyResponse(result=result)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/docs-update")
def docs_update():
    """Trivial docstring update for demo purposes."""
    return {"docs": "updated"}
