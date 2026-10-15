# orders-service/eventos.py
# Publicador de eventos hacia RabbitMQ (coreografia: orders no conoce a quien consume).
import json
import os

import pika

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
EXCHANGE = "pedidos_eventos"


def publicar_evento(tipo_evento: str, datos: dict) -> None:
    # TODO 1: conexion con RabbitMQ
    conexion = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))

    # TODO 2: canal
    canal = conexion.channel()

    # TODO 3: exchange tipo fanout (reparte cada mensaje a todas las colas enlazadas)
    canal.exchange_declare(exchange=EXCHANGE, exchange_type="fanout")

    # TODO 4: publicar el mensaje (routing_key vacia porque es fanout)
    mensaje = {"evento": tipo_evento, "datos": datos}
    canal.basic_publish(
        exchange=EXCHANGE,
        routing_key="",
        body=json.dumps(mensaje),
    )
    print(f"[orders] Evento publicado: {tipo_evento}")

    # TODO 5: cerrar la conexion
    conexion.close()
