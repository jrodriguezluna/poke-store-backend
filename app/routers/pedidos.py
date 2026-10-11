from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Pedido, PedidoItem, Producto, Usuario
from ..schemas import PedidoHistorialOut, PedidoIn, PedidoOut

router = APIRouter(prefix="/api/pedidos", tags=["pedidos"])


@router.post("", response_model=PedidoOut, status_code=201)
def crear(datos: PedidoIn, db: Session = Depends(get_db)):
    if not db.get(Usuario, datos.usuario_id):
        raise HTTPException(400, "Usuario inexistente")

    # Une líneas repetidas del mismo producto
    cantidades: dict[int, int] = {}
    for item in datos.items:
        cantidades[item.producto_id] = cantidades.get(item.producto_id, 0) + item.cantidad

    productos = db.scalars(
        select(Producto).where(Producto.id.in_(list(cantidades)), Producto.activo.is_(True))
    ).all()
    precios = {p.id: p.precio for p in productos}

    faltantes = sorted(set(cantidades) - set(precios))
    if faltantes:
        raise HTTPException(400, f"Productos no disponibles: {faltantes}")

    total = sum(precios[pid] * cant for pid, cant in cantidades.items())  # total calculado en el servidor
    pedido = Pedido(
        usuario_id=datos.usuario_id,
        total=total,
        items=[
            PedidoItem(producto_id=pid, cantidad=cant, precio_unit=precios[pid])
            for pid, cant in cantidades.items()
        ],
    )
    db.add(pedido)
    db.commit()  # pedido e ítems se guardan en una sola transacción: o todo o nada
    return {"id": pedido.id, "total": total}


@router.get("", response_model=list[PedidoHistorialOut])
def historial(usuario_id: int = Query(alias="usuarioId"), db: Session = Depends(get_db)):
    pedidos = db.scalars(
        select(Pedido).where(Pedido.usuario_id == usuario_id).order_by(Pedido.id.desc())
    ).all()
    return [
        {
            "id": p.id,
            "total": p.total,
            "fecha": p.creado_en,
            "items": [
                {"nombre": i.producto.nombre, "cantidad": i.cantidad, "precioUnit": i.precio_unit}
                for i in p.items
            ],
        }
        for p in pedidos
    ]

