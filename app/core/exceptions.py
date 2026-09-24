from fastapi import Request, status
from fastapi.responses import JSONResponse
from app.schemas.base import APIResponse

async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=APIResponse(
            success=False,
            message="Erro interno do servidor",
            error_code="INTERNAL_ERROR"
        ).model_dump()
    )

async def custom_http_exception_handler(request: Request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content=APIResponse(
            success=False,
            message=exc.detail,
            error_code="HTTP_ERROR"
        ).model_dump()
    )
