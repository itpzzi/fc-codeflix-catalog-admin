from uuid import UUID, uuid4

import pytest

from src.core.video.domain.value_objects import MediaStatus, MediaType
from src.core.video.infra.process_audio_video_media_deserializer import (
    ProcessAudioVideoMediaDeserializer,
    UseCaseInput,
)


def test_is_valid_success_completed():
    data = {
        "error": "",
        "status": "COMPLETED",
        "video": {
            "resource_id": f"{str(uuid4())}.VIDEO",
            "encoded_video_folder": "/media/video",
        },
    }
    deserializer = ProcessAudioVideoMediaDeserializer(data, UseCaseInput)
    assert deserializer.is_valid() is True

    instance = deserializer.instance
    assert instance.media_status == MediaStatus.COMPLETED
    assert instance.media_type == MediaType.VIDEO
    assert isinstance(instance.video_id, UUID)
    assert instance.encoded_location == "/media/video"


def test_is_valid_some_encoder_failure_status():
    data = {
        "error": "some encoder failure",
        "status": "ERROR",
        "video": {
            "resource_id": f"{str(uuid4())}.VIDEO",
            "encoded_video_folder": "/media/error",
        },
    }
    deserializer = ProcessAudioVideoMediaDeserializer(data, UseCaseInput)
    assert deserializer.is_valid() is True

    instance = deserializer.instance
    assert instance.media_status == MediaStatus.ERROR
    assert instance.media_type == MediaType.VIDEO
    assert isinstance(instance.video_id, UUID)
    assert instance.encoded_location == "/media/error"


def test_deserializer_invalid_uuid_raises():
    data = {
        "error": "",
        "status": "COMPLETED",
        "video": {
            "resource_id": "not-a-uuid.VIDEO",
            "encoded_video_folder": "/media/broken",
        },
    }
    deserializer = ProcessAudioVideoMediaDeserializer(data, UseCaseInput)
    with pytest.raises(ValueError):
        deserializer.is_valid(raise_exception=True)


def test_deserializer_missing_encoded_location_raises():
    data = {
        "error": "",
        "status": "COMPLETED",
        "video": {
            "resource_id": f"{str(uuid4())}.VIDEO",
        },
    }
    deserializer = ProcessAudioVideoMediaDeserializer(data, UseCaseInput)
    with pytest.raises(ValueError, match="location cannot be empty"):
        deserializer.is_valid(raise_exception=True)
