# gateway-service/main.py
# API GATEWAY: unico punto de entrada al sistema (puerto 8100).
# Reenvia (proxy) cada peticion al microservicio correspondiente.

import os

from fastapi import FastAPI, Request
import httpx

app = FastAPI(title="API Gateway - FastBite")

# TODO 1: define un diccionario con la URL base de cada microservicio:
RUTAS = {
    "usuarios": os.getenv("USERS_SERVICE_URL", "http://localhost:8101"),
    "menu": os.getenv("MENU_SERVICE_URL", "http://localhost:8102"),
    "pedidos": os.getenv("ORDERS_SERVICE_URL", "http://localhost:8103"),
}

@app.api_route("/api/{servicio}/{ruta_resto:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def gateway(servicio: str, ruta_resto: str, request: Request):
    if servicio not in RUTAS:
        return {"error": "servicio no encontrado"}

    url_destino = f"{RUTAS[servicio]}/{ruta_resto}"

    async with httpx.AsyncClient() as client:
        respuesta = await client.request(request.method, url_destino, content=await request.body())
    return respuesta.json()
