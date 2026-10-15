# ESTE ARCHIVO SE AGREGA/INTEGRA AL orders-service YA EXISTENTE (Semana 3)
# Implementa CQRS (separa comandos de consultas) + Event Sourcing (el estado
# se reconstruye a partir de eventos, no se guarda directamente).

# TODO 1: crea una lista global "event_store = []" que sera el almacen de eventos

event_store = []

def comando_crear_pedido(usuario: str, items: list):
    """
    LADO DEL COMANDO (escritura).
    En vez de guardar el pedido final directamente, se guarda un EVENTO.
    """
    evento = {"tipo": "PedidoCreado", "datos": {"usuario": usuario, "items": items}}
    event_store.append(evento)
    return {"status": "evento registrado"}

def comando_cancelar_pedido(pedido_id: int):
    """Otro comando: agrega un evento PedidoCancelado."""
    event_store.append({"tipo": "PedidoCancelado", "datos": {"pedido_id": pedido_id}})
    return {"status": "evento registrado"}

def consulta_resumen_pedidos():
    """
    LADO DE LA CONSULTA (lectura).
    Reconstruye el estado actual RECORRIENDO (replaying) todos los eventos guardados.
    Este modelo de lectura es DISTINTO a como se guardaron los datos.
    """
    resumen = []
    for evento in event_store:
        if evento["tipo"] == "PedidoCreado":
            resumen.append({
                "id": len(resumen) + 1,
                "usuario": evento["datos"]["usuario"],
                "items": evento["datos"]["items"],
                "estado": "creado",
            })
        elif evento["tipo"] == "PedidoCancelado":
            pedido_id = evento["datos"]["pedido_id"]
            for pedido in resumen:
                if pedido["id"] == pedido_id:
                    pedido["estado"] = "cancelado"
    return resumen
