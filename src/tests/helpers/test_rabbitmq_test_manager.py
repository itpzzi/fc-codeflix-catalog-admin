import json
from unittest.mock import Mock, patch

import pytest

from src.tests.helpers.rabbitmq_test_manager import RabbitMQTestManager


class TestRabbitMQTestManager:
    """Testes unitários para RabbitMQTestManager usado em testes E2E"""

    @pytest.fixture
    def manager(self):
        """Fixture que cria uma instância do RabbitMQTestManager"""
        return RabbitMQTestManager(host="test-host")

    @pytest.fixture
    def mock_connection(self):
        """Mock da conexão RabbitMQ"""
        connection = Mock()
        connection.is_closed = False
        return connection

    @pytest.fixture
    def mock_channel(self):
        """Mock do canal RabbitMQ"""
        channel = Mock()
        return channel

    @patch.dict("os.environ", {}, clear=False)
    @patch("os.environ.get")
    def test_init_sets_default_values(self, mock_get):
        """Testa se a inicialização define valores padrão corretos"""
        mock_get.return_value = "some-host"
        manager = RabbitMQTestManager()

        assert manager.host == "some-host"
        assert manager.connection is None
        assert manager.channel is None
        assert manager.queues_to_cleanup == []

    def test_init_with_custom_host(self):
        """Testa inicialização com host customizado"""
        custom_host = "custom-rabbitmq-host"
        manager = RabbitMQTestManager(host=custom_host)

        assert manager.host == custom_host

    @patch("pika.BlockingConnection")
    @patch("pika.ConnectionParameters")
    def test_setup_connection_success(
        self, mock_params, mock_connection_class, manager
    ):
        """Testa conexão bem-sucedida"""
        mock_connection = Mock()
        mock_channel = Mock()
        mock_connection.channel.return_value = mock_channel
        mock_connection_class.return_value = mock_connection

        result = manager.setup_connection()

        assert result is True
        assert manager.connection == mock_connection
        assert manager.channel == mock_channel
        mock_params.assert_called_once_with(host="test-host")
        mock_connection_class.assert_called_once()

    @patch("pika.BlockingConnection")
    def test_setup_connection_failure(self, mock_connection_class, manager):
        """Testa falha na conexão"""
        mock_connection_class.side_effect = Exception("Connection failed")

        result = manager.setup_connection()

        assert result is False
        assert manager.connection is None
        assert manager.channel is None

    def test_create_and_purge_queue_without_connection(self, manager):
        """Testa criação de fila sem conexão estabelecida"""
        with pytest.raises(Exception, match="Conexão não estabelecida"):
            manager.create_and_purge_queue("test-queue")

    def test_create_and_purge_queue_success(self, manager, mock_channel):
        """Testa criação e limpeza de fila com sucesso"""
        manager.channel = mock_channel
        queue_name = "test-queue"

        manager.create_and_purge_queue(queue_name)

        mock_channel.queue_declare.assert_called_once_with(
            queue=queue_name, durable=True
        )
        mock_channel.queue_purge.assert_called_once_with(queue=queue_name)
        assert queue_name in manager.queues_to_cleanup

    def test_publish_message_without_connection(self, manager):
        """Testa publicação de mensagem sem conexão"""
        with pytest.raises(Exception, match="Conexão não estabelecida"):
            manager.publish_message("test-queue", {"test": "message"})

    @patch("pika.BasicProperties")
    def test_publish_message_success(
        self, mock_properties_class, manager, mock_channel
    ):
        """Testa publicação de mensagem com sucesso"""
        manager.channel = mock_channel
        mock_properties = Mock()
        mock_properties_class.return_value = mock_properties

        queue_name = "test-queue"
        message = {"test": "message"}

        manager.publish_message(queue_name, message)

        mock_properties_class.assert_called_once_with(delivery_mode=2)
        mock_channel.basic_publish.assert_called_once_with(
            exchange="",
            routing_key=queue_name,
            body=json.dumps(message),
            properties=mock_properties,
        )

    def test_get_message_count_without_connection(self, manager):
        """Testa contagem de mensagens sem conexão"""
        result = manager.get_message_count("test-queue")
        assert result == 0

    def test_get_message_count_success(self, manager, mock_channel):
        """Testa contagem de mensagens com sucesso"""
        manager.channel = mock_channel
        mock_method = Mock()
        mock_method.method.message_count = 5
        mock_channel.queue_declare.return_value = mock_method

        result = manager.get_message_count("test-queue")

        assert result == 5
        mock_channel.queue_declare.assert_called_once_with(
            queue="test-queue", durable=True, passive=True
        )

    def test_consume_message_without_connection(self, manager):
        """Testa consumo de mensagem sem conexão"""
        result = manager.consume_message("test-queue")
        assert result is None

    @patch("time.time")
    def test_consume_message_timeout(
        self, mock_time, manager, mock_channel, mock_connection
    ):
        """Testa timeout no consumo de mensagem"""
        manager.channel = mock_channel
        manager.connection = mock_connection

        mock_time.side_effect = [0, 6]

        result = manager.consume_message("test-queue", timeout=5)

        assert result is None
        mock_channel.basic_consume.assert_called_once()

    def test_consume_message_success(self, manager, mock_channel, mock_connection):
        """Testa consumo de mensagem com sucesso"""
        manager.channel = mock_channel
        manager.connection = mock_connection

        test_message = {"test": "data"}

        def mock_basic_consume(queue, on_message_callback):

            mock_method = Mock()
            mock_method.delivery_tag = "test-tag"
            mock_properties = Mock()

            on_message_callback(
                mock_channel,
                mock_method,
                mock_properties,
                json.dumps(test_message).encode(),
            )

        mock_channel.basic_consume.side_effect = mock_basic_consume

        mock_connection.process_data_events.return_value = None

        result = manager.consume_message("test-queue", timeout=5)

        assert result == test_message
        mock_channel.basic_ack.assert_called_once_with(delivery_tag="test-tag")

    def test_consume_message_json_decode_error(
        self, manager, mock_channel, mock_connection
    ):
        """Testa erro de decodificação JSON no consumo"""
        manager.channel = mock_channel
        manager.connection = mock_connection

        def mock_basic_consume(queue, on_message_callback):
            mock_method = Mock()
            mock_method.delivery_tag = "test-tag"
            mock_properties = Mock()

            on_message_callback(
                mock_channel, mock_method, mock_properties, b"invalid-json"
            )

        mock_channel.basic_consume.side_effect = mock_basic_consume
        mock_connection.process_data_events.return_value = None

        result = manager.consume_message("test-queue", timeout=5)

        assert result is None
        mock_channel.basic_nack.assert_called_once_with(delivery_tag="test-tag")

    def test_cleanup_with_queues(self, manager, mock_channel, mock_connection):
        """Testa limpeza com filas para limpar"""
        manager.channel = mock_channel
        manager.connection = mock_connection
        manager.queues_to_cleanup = ["queue1", "queue2"]

        manager.cleanup()

        assert mock_channel.queue_purge.call_count == 2
        mock_channel.queue_purge.assert_any_call(queue="queue1")
        mock_channel.queue_purge.assert_any_call(queue="queue2")
        mock_connection.close.assert_called_once()

    def test_cleanup_with_queue_purge_error(
        self, manager, mock_channel, mock_connection
    ):
        """Testa limpeza com erro na purga de fila"""
        manager.channel = mock_channel
        manager.connection = mock_connection
        manager.queues_to_cleanup = ["queue1"]

        mock_channel.queue_purge.side_effect = Exception("Purge failed")

        manager.cleanup()

        mock_connection.close.assert_called_once()

    def test_cleanup_without_connection(self, manager):
        """Testa limpeza sem conexão estabelecida"""

        manager.cleanup()

    def test_cleanup_with_closed_connection(self, manager, mock_channel):
        """Testa limpeza com conexão já fechada"""
        manager.channel = mock_channel
        mock_connection = Mock()
        mock_connection.is_closed = True
        manager.connection = mock_connection

        manager.cleanup()

        mock_connection.close.assert_not_called()


class TestRabbitMQTestManagerIntegration:
    """Testes de integração simulando uso em testes E2E"""

    @pytest.fixture
    def manager_with_mocks(self):
        """Manager com mocks configurados para simular uso em E2E"""
        manager = RabbitMQTestManager()

        with patch("pika.BlockingConnection") as mock_conn_class, patch(
            "pika.ConnectionParameters"
        ):

            mock_connection = Mock()
            mock_channel = Mock()
            mock_connection.channel.return_value = mock_channel
            mock_connection.is_closed = False
            mock_conn_class.return_value = mock_connection

            manager.setup_connection()

            yield manager, mock_channel, mock_connection
