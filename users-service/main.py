# users-service/main.py
# Microservicio independiente de usuarios. Corre en el puerto 8101.
from fastapi import FastAPI

app = FastAPI(title="Users Service")

usuarios = [
    {"id": 1, "nombre": "Juan"},
    {"id": 2, "nombre": "Maria"},
    {"id": 3, "nombre": "Carlos"},
]


@app.get("/usuarios/{usuario_id}")
def obtener_usuario(usuario_id: int):
    for u in usuarios:
        if u["id"] == usuario_id:
            return u
    return {"error": "no encontrado"}


@app.get("/usuarios")
def listar_usuarios():
    return usuarios
