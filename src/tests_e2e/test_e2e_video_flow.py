import signal
import subprocess
import time

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from rest_framework import status
from rest_framework.test import APIClient

from src.django_project.video_app.models import Video as VideoModel
from src.tests.helpers.rabbitmq_test_manager import RabbitMQTestManager


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def movie_category_data():
    return dict(name="movie category", description="movie category description")


@pytest.fixture
def drama_genre_data_factory():
    return lambda categories: dict(
        name="drama genre",
        categories=[str(category_id) for category_id in list(categories)],
        is_active=True,
    )


@pytest.fixture
def steve_crafter_cast_member_data():
    return dict(name="steve crafter", type="director")


@pytest.fixture
def craft_movie_data_factory():
    return lambda cast_ids, genre_ids, category_ids: dict(
        title="Craft Movie",
        description="test description",
        duration=10,
        launch_year=2019,
        rating="L",
        opened=True,
        cast_members=list(cast_ids) if cast_ids else [],
        genres=list(genre_ids) if genre_ids else [],
        categories=list(category_ids) if category_ids else [],
    )


@pytest.fixture
def dummy_video_file():
    dummy_content = b"dummy mp4 content"
    file_name = "test_video.mp4"
    content_type = "video/mp4"
    return SimpleUploadedFile(
        name=file_name,
        content=dummy_content,
        content_type=content_type,
    )


@pytest.fixture
def rabbitmq_test_manager():
    return RabbitMQTestManager()


def stop_consumer_process(process):
    process.send_signal(signal.SIGINT)
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()


@pytest.mark.django_db
class TestE2E2ETestUserCanProcessAndPublishCompletedVideo:
    @pytest.mark.integration
    def test_full_video_flow(
        self,
        api_client,
        movie_category_data,
        drama_genre_data_factory,
        steve_crafter_cast_member_data,
        craft_movie_data_factory,
        dummy_video_file,
        rabbitmq_test_manager,
    ):
        assert (
            rabbitmq_test_manager.setup_connection()
        ), "Falha ao conectar com RabbitMQ."

        rabbitmq_test_manager.create_and_purge_queue("videos.new")
        rabbitmq_test_manager.create_and_purge_queue("videos.converted")

        try:
            self._log("🎬 Iniciando teste E2E completo do fluxo de vídeo.")

            category_id = self._create_category(api_client, movie_category_data)
            self._log(f"✅ Categoria criada | 🏷️ ID: {category_id}")
            genre_id = self._create_genre(
                api_client, drama_genre_data_factory([category_id])
            )
            self._log(f"✅ Gênero criado | 🎭 ID: {genre_id}")
            cast_member_id = self._create_cast_member(
                api_client, steve_crafter_cast_member_data
            )
            self._log(f"✅ Elenco criado | 🎬 ID: {cast_member_id}")

            video_id = self._create_video_metadata(
                api_client,
                craft_movie_data_factory([cast_member_id], [genre_id], [category_id]),
            )
            self._log(f"✅ Vídeo criado (sem mídia) | 📽️ ID: {video_id}")

            self._upload_video_file(api_client, video_id, dummy_video_file)
            self._log(f"✅ Vídeo atualizado (com mídia) | 📽️ ID: {video_id}")

            resource_id = self._verify_new_video_event_published(
                rabbitmq_test_manager, video_id
            )
            self._log(f"✅ Evento verificado na fila | 📨 Resource ID: {resource_id}")

            self._simulate_encoder_completion(rabbitmq_test_manager, video_id)
            self._log(
                f"🎬 Simulado: Encoder publicou mensagem de conclusão para {video_id}"
            )

            self._wait_for_video_processing_completion(video_id)

            self._assert_video_is_published(video_id)

            self._log("🎉 Teste E2E concluído com sucesso!")

        finally:
            rabbitmq_test_manager.cleanup()
            self._display_all_logs()

    def setup_method(self):
        self.logs = []

    def _log(self, message):
        self.logs.append(message)
        print(message)

    def _display_all_logs(self):
        print("\n" + "=" * 50)
        print("[ EXECUTION LOGS ]")
        print("=" * 50)
        for entry in self.logs:
            print(entry)
        print("=" * 50)

    def _create_category(self, client, data):
        response = client.post("/api/categories/", data=data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        return response.data.get("id")

    def _create_genre(self, client, data):
        response = client.post("/api/genres/", data=data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        return response.data.get("id")

    def _create_cast_member(self, client, data):
        response = client.post("/api/cast_members/", data=data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        return response.data.get("id")

    def _create_video_metadata(self, client, data):
        response = client.post("/api/videos/", data=data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        return response.data.get("id")

    def _upload_video_file(self, client, video_id, video_file):
        data = {"video_file": video_file}
        response = client.patch(
            f"/api/videos/{video_id}/", data=data, format="multipart"
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def _verify_new_video_event_published(
        self, rabbitmq_manager, video_id, queue_name="videos.new"
    ):
        time.sleep(1)
        message = rabbitmq_manager.consume_message(queue_name)
        assert message is not None, f"No message found in queue '{queue_name}'"
        assert message["resource_id"] == f"{video_id}.VIDEO"
        assert f"videos/{video_id}/" in message["file_path"]
        return message["resource_id"]

    def _simulate_encoder_completion(
        self, rabbitmq_manager, video_id, queue_name="videos.converted"
    ):
        encoded_message = {
            "error": "",
            "status": "COMPLETED",
            "video": {
                "resource_id": f"{video_id}.VIDEO",
                "encoded_video_folder": f"/path/to/encoded/video/{video_id}",
            },
        }
        rabbitmq_manager.publish_message(queue_name, encoded_message)

    def _wait_for_video_processing_completion(self, video_id, timeout_seconds=10):
        self._log(f"🚀 Iniciando consumer para processamento do vídeo {video_id}...")
        call_command("startconsumer", "--once")
        self._log(
            f"⌛ Aguardando até {timeout_seconds} segundos para verificar o status do vídeo..."
        )
        time.sleep(timeout_seconds)

    def _assert_video_is_published(self, video_id):
        self._log(f"🔍 Verificando status final do vídeo {video_id}...")
        video = VideoModel.objects.get(id=video_id)
        assert video.published is True, "Vídeo não foi publicado."
        assert video.video is not None, "Vídeo não possui mídia."
        assert (
            video.video.status == "MediaStatus.COMPLETED"
        ), "Vídeo não está marcado como completo."
        self._log(f"✅ Vídeo {video_id} verificado e publicado com sucesso.")
