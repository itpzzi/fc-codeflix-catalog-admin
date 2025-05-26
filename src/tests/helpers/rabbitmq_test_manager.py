import json
import os
import time

import pika


class RabbitMQTestManager:
    def __init__(self, host=None):
        self.host = host or os.environ.get("RABBITMQ_HOST", "rabbitmq")
        self.connection = None
        self.channel = None
        self.queues_to_cleanup = []

    def setup_connection(self):
        print(f"setup_connection: {self.host}")
        try:
            connection_params = pika.ConnectionParameters(host=self.host)
            self.connection = pika.BlockingConnection(connection_params)
            self.channel = self.connection.channel()
            return True
        except Exception as e:
            print(f"❌ Falha ao conectar com RabbitMQ: {e}")
            return False

    def create_and_purge_queue(self, queue_name):
        print(f"create_and_purge_queue: {self.host}")
        if not self.channel:
            raise Exception("Conexão não estabelecida")

        self.channel.queue_declare(queue=queue_name, durable=True)
        self.channel.queue_purge(queue=queue_name)
        self.queues_to_cleanup.append(queue_name)
        print(f"🧹 Fila '{queue_name}' criada e limpa")

    def publish_message(self, queue_name, message):
        print(f"publish_message: {self.host}")
        if not self.channel:
            raise Exception("Conexão não estabelecida")

        properties = pika.BasicProperties(delivery_mode=2)
        self.channel.basic_publish(
            exchange="",
            routing_key=queue_name,
            body=json.dumps(message),
            properties=properties,
        )
        print(f"📤 Mensagem enviada para '{queue_name}': {message}")

    def get_message_count(self, queue_name):
        print(f"get_message_count: {self.host}")
        if not self.channel:
            return 0

        method = self.channel.queue_declare(
            queue=queue_name, durable=True, passive=True
        )
        return method.method.message_count

    def consume_message(self, queue_name, timeout=5):
        print(f"consume_message: {self.host}")
        if not self.channel:
            return None

        messages = []

        def callback(ch, method, properties, body):
            try:
                message = json.loads(body)
                messages.append(message)
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                print(f"❌ Erro ao processar mensagem: {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag)

        self.channel.basic_consume(queue=queue_name, on_message_callback=callback)

        start_time = time.time()
        while len(messages) == 0 and (time.time() - start_time) < timeout:
            self.connection.process_data_events(time_limit=1)

        return messages[0] if messages else None

    def cleanup(self):
        print(f"cleanup: {self.host}")
        if self.channel:
            for queue_name in self.queues_to_cleanup:
                try:
                    self.channel.queue_purge(queue=queue_name)
                    print(f"🧹 Fila '{queue_name}' limpa")
                except Exception as e:
                    print(f"⚠️ Erro ao limpar fila '{queue_name}': {e}")

        if self.connection and not self.connection.is_closed:
            self.connection.close()
            print("🔌 Conexão RabbitMQ fechada")
