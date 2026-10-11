from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.orm import Session
from starlette.exceptions import HTTPException as StarletteHTTPException

from .config import settings
from .database import get_db
from .routers import contacto, pedidos, productos, usuarios

Path(settings.upload_dir).mkdir(exist_ok=True)

app = FastAPI(title="poke-store API", version="1.0.0")

# Con el proxy de Vite no hace falta, pero no estorba si el front llama directo al :8000
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)


# El frontend (src/api/http.js) lee { error: "..." }; FastAPI entrega { detail: ... } por defecto.
@app.exception_handler(StarletteHTTPException)
async def error_http(_request, exc: StarletteHTTPException):
    return JSONResponse({"error": exc.detail}, status_code=exc.status_code)


@app.exception_handler(RequestValidationError)
async def error_validacion(_request, exc: RequestValidationError):
    campos = ", ".join(".".join(str(p) for p in e["loc"][1:]) for e in exc.errors())
    return JSONResponse({"error": f"Datos inválidos: {campos}"}, status_code=422)


@app.get("/api/health", tags=["sistema"])
def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))  # falla (500) si no hay conexión con RDS
    return {"ok": True}


app.include_router(productos.router)
app.include_router(usuarios.router)
app.include_router(pedidos.router)
app.include_router(contacto.router)
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

