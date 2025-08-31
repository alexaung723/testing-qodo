"""
This module contains models for the multiply endpoint.
"""

# Trivial refactor: add a comment for demo purposes

from pydantic import BaseModel

class MultiplyRequest(BaseModel):
    a: int
    b: int

class MultiplyResponse(BaseModel):
    result: int
