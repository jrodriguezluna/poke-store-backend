from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Usuario
from ..schemas import LoginIn, RegistroIn, UsuarioOut, UsuarioUpdate
from ..security import hash_password, verify_password

router = APIRouter(prefix="/api", tags=["usuarios"])


@router.post("/registro", response_model=UsuarioOut, status_code=201)
def registro(datos: RegistroIn, db: Session = Depends(get_db)):
    email = datos.email.lower()
    if db.scalar(select(Usuario).where(Usuario.email == email)):
        raise HTTPException(409, "El correo ya está registrado")
    usuario = Usuario(
        nombre=datos.nombre.strip(),
        email=email,
        telefono=(datos.telefono or "").strip() or None,
        direccion=datos.direccion.strip(),
        region=datos.region,
        comuna=datos.comuna,
        password_hash=hash_password(datos.password),
        rol="cliente",  # el rol nunca viene del cliente
    )
    db.add(usuario)
    try:
        db.commit()
    except IntegrityError:  # carrera entre dos registros simultáneos
        db.rollback()
        raise HTTPException(409, "El correo ya está registrado")
    db.refresh(usuario)
    return usuario


@router.post("/login", response_model=UsuarioOut)
def login(datos: LoginIn, db: Session = Depends(get_db)):
    usuario = db.scalar(select(Usuario).where(Usuario.email == datos.email.lower()))
    # Mismo mensaje para "no existe" y "clave incorrecta": no revela qué correos están registrados
    if not usuario or not verify_password(datos.password, usuario.password_hash):
        raise HTTPException(401, "Credenciales inválidas")
    return usuario


@router.get("/usuarios", response_model=list[UsuarioOut])
def listar(db: Session = Depends(get_db)):
    return db.scalars(select(Usuario).order_by(Usuario.id)).all()


@router.put("/usuarios/{usuario_id}", response_model=UsuarioOut)
def modificar(usuario_id: int, datos: UsuarioUpdate, db: Session = Depends(get_db)):
    usuario = db.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(404, "Usuario no encontrado")

    usuario.nombre = datos.nombre.strip()
    usuario.email = datos.email.lower()
    usuario.telefono = (datos.telefono or "").strip() or None
    usuario.direccion = datos.direccion.strip()
    usuario.region = datos.region
    usuario.comuna = datos.comuna
    usuario.rol = datos.rol
    if datos.password:
        usuario.password_hash = hash_password(datos.password)

    try:
        db.commit()
    except IntegrityError:  # email repetido
        db.rollback()
        raise HTTPException(409, "El correo ya está registrado")
    db.refresh(usuario)
    return usuario


@router.delete("/usuarios/{usuario_id}", status_code=204)
def eliminar(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(404, "Usuario no encontrado")
    try:
        db.delete(usuario)
        db.commit()
    except IntegrityError:  # tiene pedidos asociados
        db.rollback()
        raise HTTPException(409, "No se puede eliminar: el usuario tiene pedidos")
    return Response(status_code=204)