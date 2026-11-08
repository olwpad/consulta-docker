import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

DB_PATH = Path(os.getenv("DATABASE_PATH", "/data/consulta.db"))
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="API de consulta", version="1.0.0", description="API pequeña de ejemplo con SQLite")


@contextmanager
def connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


class ItemInput(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    descripcion: str = Field(default="", max_length=500)


def init_db() -> None:
    with connection() as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                descripcion TEXT NOT NULL DEFAULT ''
            )"""
        )
        count = conn.execute("SELECT COUNT(*) FROM items").fetchone()[0]
        if count == 0:
            conn.executemany(
                "INSERT INTO items (nombre, descripcion) VALUES (?, ?)",
                [
                    ("Teclado", "Teclado mecánico de ejemplo"),
                    ("Mouse", "Mouse inalámbrico de ejemplo"),
                    ("Monitor", "Monitor de 24 pulgadas de ejemplo"),
                ],
            )


@app.on_event("startup")
def startup() -> None:
    init_db()


def serialize(row: sqlite3.Row) -> dict[str, Any]:
    return {"id": row["id"], "nombre": row["nombre"], "descripcion": row["descripcion"]}


@app.get("/health")
def health() -> dict[str, str]:
    return {"estado": "ok"}


@app.get("/items")
def list_items() -> list[dict[str, Any]]:
    with connection() as conn:
        rows = conn.execute("SELECT id, nombre, descripcion FROM items ORDER BY id").fetchall()
    return [serialize(row) for row in rows]


@app.get("/items/{item_id}")
def get_item(item_id: int) -> dict[str, Any]:
    with connection() as conn:
        row = conn.execute(
            "SELECT id, nombre, descripcion FROM items WHERE id = ?", (item_id,)
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Elemento no encontrado")
    return serialize(row)


@app.post("/items", status_code=201)
def create_item(item: ItemInput) -> dict[str, Any]:
    with connection() as conn:
        cursor = conn.execute(
            "INSERT INTO items (nombre, descripcion) VALUES (?, ?)",
            (item.nombre, item.descripcion),
        )
        row = conn.execute(
            "SELECT id, nombre, descripcion FROM items WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
    return serialize(row)
