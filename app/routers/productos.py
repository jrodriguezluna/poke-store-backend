from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..models import Producto
from ..schemas import ProductoIn, ProductoOut

router = APIRouter(prefix="/api/productos", tags=["productos"])


def borrar_imagen_local(ruta: str | None) -> None:
    # Solo se borran archivos que subimos nosotros; .name evita rutas tipo ../../
    if ruta and ruta.startswith("/uploads/"):
        (Path(settings.upload_dir) / Path(ruta).name).unlink(missing_ok=True)


def validar_imagen(url: str | None) -> str | None:
    url = (url or "").strip() or None
    if url and not url.startswith(("http://", "https://")):
        raise HTTPException(400, "La URL de la imagen debe comenzar con http:// o https://")
    return url


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
def crear(datos: ProductoIn, db: Session = Depends(get_db)):
    p = Producto(
        nombre=datos.nombre.strip(),
        categoria=datos.categoria,
        precio=datos.precio,
        descripcion=datos.descripcion,
        stock=datos.stock,
        imagen=validar_imagen(datos.imagen),
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@router.put("/{producto_id}", response_model=ProductoOut)
def actualizar(producto_id: int, datos: ProductoIn, db: Session = Depends(get_db)):
    p = db.get(Producto, producto_id)
    if not p or not p.activo:
        raise HTTPException(404, "Producto no encontrado")

    imagen = validar_imagen(datos.imagen)
    if imagen != p.imagen:
        borrar_imagen_local(p.imagen)
        p.imagen = imagen

    p.nombre, p.categoria, p.precio = datos.nombre.strip(), datos.categoria, datos.precio
    p.descripcion, p.stock = datos.descripcion, datos.stock
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

