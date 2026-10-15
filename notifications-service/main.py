# notifications-service/main.py
# Consumidor de eventos: reacciona a "PedidoCreado" sin que orders-service lo llame.
import json
import os

import pika

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
EXCHANGE = "pedidos_eventos"


def callback(ch, method, properties, body):
    # TODO 1: si el evento es "PedidoCreado", imprime la notificacion
    mensaje = json.loads(body)
    if mensaje["evento"] == "PedidoCreado":
        datos = mensaje["datos"]
        print(
            f"[notifications] Notificacion: pedido #{datos['pedido_id']} "
            f"del usuario {datos['usuario_id']} creado "
            f"(total ${datos['monto_total']}, pago: {datos['metodo_pago']})"
        )


def main():
    # TODO 2: conexion
    conexion = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))

    # TODO 3: canal
    canal = conexion.channel()

    # TODO 4: exchange (mismo nombre y tipo que el publicador)
    canal.exchange_declare(exchange=EXCHANGE, exchange_type="fanout")

    # TODO 5: cola temporal (exclusive: se borra al desconectarse)
    resultado = canal.queue_declare(queue="", exclusive=True)
    nombre_cola = resultado.method.queue

    # TODO 6: enlazar la cola al exchange
    canal.queue_bind(exchange=EXCHANGE, queue=nombre_cola)

    # TODO 7: consumir mensajes
    canal.basic_consume(queue=nombre_cola, on_message_callback=callback, auto_ack=True)

    print("Esperando eventos... (CTRL+C para salir)")
    try:
        canal.start_consuming()
    except KeyboardInterrupt:
        print("\nNotifications-service detenido.")
        conexion.close()


if __name__ == "__main__":
    main()
