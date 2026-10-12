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

    productos_map: dict[int, Producto] = {p.id: p for p in db.scalars(
        select(Producto).where(Producto.id.in_(list(cantidades)), Producto.activo.is_(True))
    ).all()}

    # Verificar que todos los productos solicitados existan
    faltantes = sorted(set(cantidades) - set(productos_map))
    if faltantes:
        raise HTTPException(400, f"Productos no disponibles: {faltantes}")

    # Verificar stock suficiente para cada producto antes de comprometer nada
    sin_stock = [
        productos_map[pid].nombre
        for pid, cant in cantidades.items()
        if productos_map[pid].stock < cant
    ]
    if sin_stock:
        raise HTTPException(400, f"Stock insuficiente para: {', '.join(sin_stock)}")

    # Descontar stock y calcular total (todo dentro de la misma transacción)
    total = 0
    for pid, cant in cantidades.items():
        p = productos_map[pid]
        p.stock -= cant
        total += p.precio * cant

    pedido = Pedido(
        usuario_id=datos.usuario_id,
        total=total,
        items=[
            PedidoItem(producto_id=pid, cantidad=cant, precio_unit=productos_map[pid].precio)
            for pid, cant in cantidades.items()
        ],
    )
    db.add(pedido)
    db.commit()  # pedido, ítems y descuento de stock se guardan en una sola transacción: o todo o nada
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

