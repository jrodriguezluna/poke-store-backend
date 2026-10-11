from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import MensajeContacto
from ..schemas import ContactoIn

router = APIRouter(prefix="/api/contacto", tags=["contacto"])


@router.post("", status_code=201)
def enviar(datos: ContactoIn, db: Session = Depends(get_db)):
    db.add(MensajeContacto(nombre=datos.nombre.strip(), email=datos.email, mensaje=datos.mensaje.strip()))
    db.commit()
    return {"ok": True}

