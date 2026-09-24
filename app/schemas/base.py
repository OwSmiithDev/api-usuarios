from pydantic import BaseModel
from typing import Generic, TypeVar, Optional, List

T = TypeVar("T")

class APIResponse(BaseModel, Generic[T]):
    success: bool
    data: Optional[T] = None
    message: Optional[str] = None
    error_code: Optional[str] = None

class PaginatedData(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    limit: int
    pages: int
