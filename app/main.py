from fastapi import Depends, FastAPI, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.core.config import get_settings
from app.database.session import Base, SessionLocal, engine
from app.routes.admin_users import router as admin_users_router
from app.routes.auth import router as auth_router
from app.routes.catalog import authors_router, books_router, categories_router
from app.routes.loans import router as loans_router
from app.services.seed import seed_database

settings = get_settings()

async def add_common_headers(request: Request, response: Response) -> None:
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    origin = request.headers.get("origin")
    if origin in settings.cors_origin_list:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"


app = FastAPI(title=settings.app_name, version="1.0.0", dependencies=[Depends(add_common_headers)])


@app.exception_handler(IntegrityError)
async def integrity_error_handler(_: Request, __: IntegrityError):
    return JSONResponse(status_code=409, content={"detail": "Database constraint violation"})


@app.on_event("startup")
async def startup() -> None:
    Base.metadata.create_all(bind=engine)
    if settings.seed_database:
        with SessionLocal() as db:
            seed_database(db)


@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok", "app": settings.app_name}


@app.options("/{full_path:path}", include_in_schema=False)
async def cors_preflight(full_path: str, request: Request, response: Response):
    origin = request.headers.get("origin")
    if origin in settings.cors_origin_list:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,PATCH,DELETE,OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Authorization,Content-Type"
    return {}


app.include_router(auth_router)
app.include_router(admin_users_router)
app.include_router(books_router)
app.include_router(authors_router)
app.include_router(categories_router)
app.include_router(loans_router)
