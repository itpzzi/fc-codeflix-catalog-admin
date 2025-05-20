from rest_framework import serializers

from src.core.video.domain.value_objects import Rating


class SetField(serializers.ListField):
    def to_internal_value(self, data):
        return set(super().to_internal_value(data))

    def to_representation(self, data):
        return list(super().to_representation(data))


class RatingField(serializers.ChoiceField):
    def __init__(self, **kwargs):
        self.enum = Rating
        choices = [(rating.name, rating.name) for rating in self.enum]
        super().__init__(choices=choices, **kwargs)

    def to_internal_value(self, data):
        value = super().to_internal_value(data)
        try:
            return self.enum[value]
        except KeyError:
            raise serializers.ValidationError(f"invalid rating: {data}")

    def to_representation(self, rating: Rating):
        return super().to_representation(rating.name)


class CreateVideoWithoutMediaDeserializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(max_length=1000)
    launch_year = serializers.IntegerField(min_value=1900, max_value=2100)
    opened = serializers.BooleanField(default=False)
    duration = serializers.FloatField(min_value=0.0, max_value=1000.0)
    rating = RatingField()
    categories = SetField(child=serializers.UUIDField())
    genres = SetField(child=serializers.UUIDField())
    cast_members = SetField(child=serializers.UUIDField())


class CreateVideoWithoutMediaSerializer(serializers.Serializer):
    id = serializers.UUIDField()


class UploadVideoDeserializer(serializers.Serializer):
    video_id = serializers.UUIDField(required=True)
    video_file = serializers.FileField(required=True)

    def to_internal_value(self, data):
        validated = super().to_internal_value(data)
        file = validated["video_file"]
        errors = {}

        self._validate_content_type(file, errors)

        if errors:
            raise serializers.ValidationError(errors)

        return {
            "video_id": validated["video_id"],
            "file_name": file.name,
            "content_type": file.content_type,
            "content": file.read(),
        }

    def _validate_content_type(self, file, errors):
        if not file.content_type.startswith("video/"):
            errors["content_type"] = f"Invalid content type: {file.content_type}"
