from datetime import datetime

from sqlalchemy import ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Usuario(Base):
    __tablename__ = "usuarios"
    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(120), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    telefono: Mapped[str | None] = mapped_column(String(20), default=None)
    direccion: Mapped[str] = mapped_column(String(200))
    region: Mapped[str] = mapped_column(String(100))
    comuna: Mapped[str] = mapped_column(String(100))
    rol: Mapped[str] = mapped_column(String(20), default="cliente")
    creado_en: Mapped[datetime] = mapped_column(server_default=func.now())


class Producto(Base):
    __tablename__ = "productos"
    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100))
    tipo: Mapped[str | None] = mapped_column(String(30), default=None)
    categoria: Mapped[str | None] = mapped_column(String(50), default=None)
    precio: Mapped[int]
    imagen: Mapped[str | None] = mapped_column(String(255), default=None)
    descripcion: Mapped[str | None] = mapped_column(Text, default=None)
    stock: Mapped[int] = mapped_column(default=0)
    activo: Mapped[bool] = mapped_column(default=True)


class Pedido(Base):
    __tablename__ = "pedidos"
    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    total: Mapped[int]
    creado_en: Mapped[datetime] = mapped_column(server_default=func.now())
    items: Mapped[list["PedidoItem"]] = relationship(
        back_populates="pedido", cascade="all, delete-orphan"
    )


class PedidoItem(Base):
    __tablename__ = "pedido_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    pedido_id: Mapped[int] = mapped_column(ForeignKey("pedidos.id"))
    producto_id: Mapped[int] = mapped_column(ForeignKey("productos.id"))
    cantidad: Mapped[int]
    precio_unit: Mapped[int]
    pedido: Mapped["Pedido"] = relationship(back_populates="items")
    producto: Mapped["Producto"] = relationship()


class MensajeContacto(Base):
    __tablename__ = "mensajes_contacto"
    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(120))
    mensaje: Mapped[str] = mapped_column(Text)
    creado_en: Mapped[datetime] = mapped_column(server_default=func.now())
