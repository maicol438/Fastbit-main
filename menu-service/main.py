# menu-service/main.py
# Microservicio independiente de menu. Corre en el puerto 8102.
from fastapi import FastAPI

app = FastAPI(title="Menu Service")

menu = [
    {"id": 1, "nombre": "Hamburguesa clasica", "precio": 18000},
    {"id": 2, "nombre": "Perro caliente", "precio": 12000},
    {"id": 3, "nombre": "Pizza personal", "precio": 15000},
    {"id": 4, "nombre": "Gaseosa", "precio": 4000},
]


@app.get("/menu/{producto_id}")
def obtener_producto(producto_id: int):
    for p in menu:
        if p["id"] == producto_id:
            return p
    return {"error": "no encontrado"}


@app.get("/menu")
def listar_menu():
    return menu
