from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ProductoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nombre: str
    tipo: str | None           # nombre interno en la BD
    categoria: str | None = None  # alias de tipo; el frontend filtra por este campo
    precio: int
    imagen: str | None
    descripcion: str | None
    stock: int

    @classmethod
    def model_validate(cls, obj, **kwargs):
        # Cuando SQLAlchemy nos pasa un ORM Producto,
        # copiamos tipo → categoria para que el frontend lo reciba con el nombre esperado
        instance = super().model_validate(obj, **kwargs)
        if instance.categoria is None:
            instance.categoria = instance.tipo
        return instance


class RegistroIn(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    email: EmailStr
    telefono: str | None = Field(default=None, max_length=20)
    direccion: str = Field(min_length=5, max_length=200)
    region: str = Field(min_length=1, max_length=100)
    comuna: str = Field(min_length=1, max_length=100)
    # bcrypt solo procesa los primeros 72 bytes; se limita para evitar errores
    password: str = Field(min_length=6, max_length=64)

class LoginIn(BaseModel):
    email: EmailStr
    password: str = Field(max_length=64)


class UsuarioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nombre: str
    email: str
    telefono: str | None = None
    direccion: str
    region: str
    comuna: str
    rol: str


class ItemIn(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    producto_id: int = Field(alias="productoId")
    cantidad: int = Field(ge=1)


class PedidoIn(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    usuario_id: int = Field(alias="usuarioId")
    items: list[ItemIn] = Field(min_length=1)


class PedidoOut(BaseModel):
    id: int
    total: int


class ItemHistorialOut(BaseModel):
    nombre: str
    cantidad: int
    precioUnit: int


class PedidoHistorialOut(BaseModel):
    id: int
    total: int
    fecha: datetime
    items: list[ItemHistorialOut]


class ContactoIn(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    email: EmailStr
    mensaje: str = Field(min_length=1, max_length=2000)

class UsuarioUpdate(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    email: EmailStr
    telefono: str | None = Field(default=None, max_length=20)
    direccion: str = Field(min_length=5, max_length=200)
    region: str = Field(min_length=1, max_length=100)
    comuna: str = Field(min_length=1, max_length=100)
    rol: str = "cliente"
    password: str | None = Field(default=None, min_length=6, max_length=64)
