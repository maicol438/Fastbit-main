# orders-service/main.py
# Microservicio de pedidos. Corre en el puerto 8103.
# Se comunica por HTTP con users-service (8101) y menu-service (8102),
# usa PLUGINS para procesar pagos (Microkernel) y publica eventos en RabbitMQ.

import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx

from plugins import pago_efectivo, pago_tarjeta
from eventos import publicar_evento
from orders_service_cqrs_extension import (
    comando_crear_pedido,
    comando_cancelar_pedido,
    consulta_resumen_pedidos,
)

app = FastAPI(title="Orders Service")

USERS_SERVICE_URL = os.getenv("USERS_SERVICE_URL", "http://localhost:8101")
MENU_SERVICE_URL = os.getenv("MENU_SERVICE_URL", "http://localhost:8102")

pedidos = []
siguiente_id = 1

PLUGINS = {
    "efectivo": pago_efectivo.procesar,
    "tarjeta": pago_tarjeta.procesar,
}


class ItemPedido(BaseModel):
    producto_id: int
    cantidad: int


class NuevoPedido(BaseModel):
    usuario_id: int
    items: list[ItemPedido]
    metodo_pago: str


@app.post("/pedidos")
def crear_pedido(pedido: NuevoPedido):
    global siguiente_id

    # Valida que el usuario existe (HTTP -> users-service)
    try:
        resp_usuario = httpx.get(f"{USERS_SERVICE_URL}/usuarios/{pedido.usuario_id}")
    except httpx.RequestError:
        raise HTTPException(503, "users-service no disponible")
    if "error" in resp_usuario.json():
        raise HTTPException(404, "Usuario no encontrado")

    # Valida cada producto (HTTP -> menu-service) y acumula el total
    monto_total = 0
    for item in pedido.items:
        try:
            resp_producto = httpx.get(f"{MENU_SERVICE_URL}/menu/{item.producto_id}")
        except httpx.RequestError:
            raise HTTPException(503, "menu-service no disponible")
        producto = resp_producto.json()
        if "error" in producto:
            raise HTTPException(404, f"Producto {item.producto_id} no encontrado")
        monto_total += producto.get("precio", 10000) * item.cantidad

    # Valida el metodo de pago
    if pedido.metodo_pago not in PLUGINS:
        raise HTTPException(400, "Metodo de pago no soportado")

    # Procesa el pago con el plugin correspondiente
    resultado_pago = PLUGINS[pedido.metodo_pago](monto_total)

    nuevo = {
        "id": siguiente_id,
        "usuario_id": pedido.usuario_id,
        "items": [i.model_dump() for i in pedido.items],
        "metodo_pago": pedido.metodo_pago,
        "pago": resultado_pago,
        "estado": "creado",
    }
    pedidos.append(nuevo)
    siguiente_id += 1

    # Publica el evento DESPUES de crear el pedido con exito.
    # Si RabbitMQ esta caido, el pedido igual se crea (el servicio no depende del broker).
    try:
        publicar_evento("PedidoCreado", {
            "pedido_id": nuevo["id"],
            "usuario_id": nuevo["usuario_id"],
            "monto_total": monto_total,
            "metodo_pago": nuevo["metodo_pago"],
        })
        
    except Exception as e:
        print(f"[orders] No se pudo publicar el evento: {e}")

    items_dict = [{"producto_id": i.producto_id, "cantidad": i.cantidad} for i in pedido.items]
    confirmacion = comando_crear_pedido(str(pedido.usuario_id), items_dict)

    return {"pedido": nuevo, "cqrs": confirmacion}


@app.get("/pedidos/resumen")
def resumen_pedidos():
    return consulta_resumen_pedidos()


@app.get("/pedidos")
def listar_pedidos():
    return pedidos
