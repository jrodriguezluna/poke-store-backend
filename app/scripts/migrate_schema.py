"""Apply additive schema changes without dropping existing data.

Run from the backend root with: python -m app.scripts.migrate_schema
"""
from sqlalchemy import inspect, text

from app.database import engine


USER_COLUMNS = {
    "telefono": "VARCHAR(20) NULL",
    "direccion": "VARCHAR(200) NOT NULL DEFAULT ''",
    "region": "VARCHAR(100) NOT NULL DEFAULT ''",
    "comuna": "VARCHAR(100) NOT NULL DEFAULT ''",
}
PRODUCT_COLUMNS = {
    "categoria": "VARCHAR(50) NULL",
}


def add_missing_columns(table: str, columns: dict[str, str]) -> list[str]:
    existing = {column["name"] for column in inspect(engine).get_columns(table)}
    missing = {name: definition for name, definition in columns.items() if name not in existing}

    if not missing:
        return []

    with engine.begin() as connection:
        for name, definition in missing.items():
            connection.execute(text(f"ALTER TABLE {table} ADD COLUMN {name} {definition}"))

    return list(missing)


def migrate() -> dict[str, list[str]]:
    added = {
        "usuarios": add_missing_columns("usuarios", USER_COLUMNS),
        "productos": add_missing_columns("productos", PRODUCT_COLUMNS),
    }

    with engine.begin() as connection:
        connection.execute(text("""
            UPDATE productos
            SET categoria = CASE
                WHEN nombre LIKE 'Peluche %' THEN 'Peluches'
                WHEN nombre LIKE 'Figura %' THEN 'Coleccionable'
                WHEN nombre LIKE 'Almohada %' THEN 'Hogar'
                ELSE categoria
            END
            WHERE categoria IS NULL
        """))

    return added


if __name__ == "__main__":
    added = migrate()
    for table, columns in added.items():
        if columns:
            print(f"{table}: columnas agregadas: {', '.join(columns)}")
    print("Migración aplicada; no se eliminaron tablas ni registros.")
