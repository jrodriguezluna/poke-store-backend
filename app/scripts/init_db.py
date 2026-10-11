"""Recrea TODAS las tablas (borra los datos) y carga el seed.
Uso:  python -m app.scripts.init_db
"""
from app import models  # noqa: F401  (registra los modelos en Base.metadata)
from app.database import Base, SessionLocal, engine
from app.models import Producto, Usuario
from app.security import hash_password

IMG = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{}.png"

PRODUCTOS = [
    ("Peluche Pikachu", "electrico", 14990, 25, "Peluche suave de Pikachu, ideal para coleccionistas.", 25),
    ("Peluche Charmander", "fuego", 13990, 4, "Charmander de felpa con cola brillante.", 18),
    ("Peluche Squirtle", "agua", 13990, 7, "Squirtle de felpa, perfecto para regalar.", 20),
    ("Peluche Bulbasaur", "planta", 13990, 1, "Bulbasaur de felpa con bulbo removible.", 15),
    ("Figura Eevee", "normal", 9990, 133, "Figura articulada de Eevee de 12 cm.", 30),
    ("Figura Charizard", "fuego", 24990, 6, "Figura de colección de Charizard de 20 cm.", 10),
    ("Almohada Snorlax", "normal", 19990, 143, "Almohada gigante de Snorlax para dormir como campeón.", 12),
    ("Peluche Jigglypuff", "hada", 11990, 39, "Jigglypuff de felpa, versión cantante.", 22),
]


def main() -> None:
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        db.add_all(
            Producto(nombre=n, tipo=t, precio=p, imagen=IMG.format(i), descripcion=d, stock=s)
            for n, t, p, i, d, s in PRODUCTOS
        )
        db.add(
            Usuario(
                nombre="Administrador",
                email="admin@pokestore.cl",
                password_hash=hash_password("admin123"),  # solo para la demo: cambiar si se publica
                rol="admin",
            )
        )
        db.commit()
    print("BD inicializada: tablas creadas, 8 productos y usuario admin insertados.")


if __name__ == "__main__":
    main()

