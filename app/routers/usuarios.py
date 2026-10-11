from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Usuario
from ..schemas import LoginIn, RegistroIn, UsuarioOut
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

