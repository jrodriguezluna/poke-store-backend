import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Response, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..models import Producto
from ..schemas import ProductoOut

router = APIRouter(prefix="/api/productos", tags=["productos"])

EXTENSIONES = {"image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp"}


def guardar_imagen(archivo: UploadFile) -> str:
    # La extensión sale del tipo MIME validado, nunca del nombre que manda el cliente
    ext = EXTENSIONES.get(archivo.content_type)
    if not ext:
        raise HTTPException(400, "Formato de imagen no permitido (usa PNG, JPG o WEBP)")
    contenido = archivo.file.read(settings.max_upload_bytes + 1)
    if len(contenido) > settings.max_upload_bytes:
        raise HTTPException(400, "La imagen supera el máximo de 2 MB")
    nombre = f"{uuid.uuid4().hex}{ext}"
    (Path(settings.upload_dir) / nombre).write_bytes(contenido)
    return f"/uploads/{nombre}"


def borrar_imagen_local(ruta: str | None) -> None:
    # Solo se borran archivos que subimos nosotros; .name evita rutas tipo ../../
    if ruta and ruta.startswith("/uploads/"):
        (Path(settings.upload_dir) / Path(ruta).name).unlink(missing_ok=True)


def resolver_imagen(archivo: UploadFile | None, url: str | None) -> str | None:
    if archivo is not None and archivo.filename:
        return guardar_imagen(archivo)
    if url:
        if not url.startswith(("http://", "https://")):
            raise HTTPException(400, "La URL de la imagen debe comenzar con http:// o https://")
        return url
    return None


@router.get("", response_model=list[ProductoOut])
def listar(db: Session = Depends(get_db)):
    consulta = select(Producto).where(Producto.activo.is_(True)).order_by(Producto.id)
    return db.scalars(consulta).all()


@router.get("/{producto_id}", response_model=ProductoOut)
def obtener(producto_id: int, db: Session = Depends(get_db)):
    p = db.get(Producto, producto_id)
    if not p or not p.activo:
        raise HTTPException(404, "Producto no encontrado")
    return p


@router.post("", response_model=ProductoOut, status_code=201)
def crear(
    nombre: str = Form(..., min_length=1, max_length=100),
    precio: int = Form(..., ge=0),
    tipo: str | None = Form(None),
    categoria: str | None = Form(None),
    descripcion: str | None = Form(None),
    stock: int = Form(0, ge=0),
    imagen_url: str | None = Form(None),
    imagen: UploadFile | None = File(None),
    db: Session = Depends(get_db),
):
    p = Producto(
        nombre=nombre.strip(),
        tipo=tipo,
        categoria=categoria,
        precio=precio,
        descripcion=descripcion,
        stock=stock,
        imagen=resolver_imagen(imagen, imagen_url),
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@router.put("/{producto_id}", response_model=ProductoOut)
def actualizar(
    producto_id: int,
    nombre: str = Form(..., min_length=1, max_length=100),
    precio: int = Form(..., ge=0),
    tipo: str | None = Form(None),
    categoria: str | None = Form(None),
    descripcion: str | None = Form(None),
    stock: int = Form(0, ge=0),
    imagen_url: str | None = Form(None),
    imagen: UploadFile | None = File(None),
    db: Session = Depends(get_db),
):
    p = db.get(Producto, producto_id)
    if not p or not p.activo:
        raise HTTPException(404, "Producto no encontrado")

    nueva = resolver_imagen(imagen, imagen_url)  # primero se guarda la nueva...
    if nueva:
        borrar_imagen_local(p.imagen)            # ...y recién después se borra la anterior
        p.imagen = nueva

    p.nombre, p.tipo, p.categoria, p.precio = nombre.strip(), tipo, categoria, precio
    p.descripcion, p.stock = descripcion, stock
    db.commit()
    db.refresh(p)
    return p


@router.delete("/{producto_id}", status_code=204)
def eliminar(producto_id: int, db: Session = Depends(get_db)):
    p = db.get(Producto, producto_id)
    if not p or not p.activo:
        raise HTTPException(404, "Producto no encontrado")
    p.activo = False  # borrado lógico: el historial de pedidos sigue intacto
    db.commit()
    return Response(status_code=204)

