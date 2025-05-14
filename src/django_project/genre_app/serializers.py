from rest_framework import serializers

from src.core._shared.config import DEFAULT_PAGE_SIZE


class ListEntityInputDeserializer(serializers.Serializer):
    order_by = serializers.CharField(default="name")
    reverse = serializers.BooleanField(default=False)
    current_page = serializers.IntegerField(default=1)
    per_page = serializers.IntegerField(default=DEFAULT_PAGE_SIZE)


class MetaSerializer(serializers.Serializer):
    total = serializers.IntegerField()
    current_page = serializers.IntegerField()
    per_page = serializers.IntegerField()


class SetField(serializers.ListField):
    def to_internal_value(self, data):
        return set(super().to_internal_value(data))

    def to_representation(self, data):
        return list(super().to_representation(data))


class GenreSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField(max_length=255)
    is_active = serializers.BooleanField()
    categories = serializers.ListField(child=serializers.UUIDField())


class ListGenreSerializer(serializers.Serializer):
    data = GenreSerializer(many=True)
    meta = MetaSerializer()


class CreateGenreDeserializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    is_active = serializers.BooleanField()
    categories = SetField(child=serializers.UUIDField())


class CreateGenreSerializer(serializers.Serializer):
    id = serializers.UUIDField()


class DeleteGenreDeserializer(serializers.Serializer):
    id = serializers.UUIDField()


class UpdateGenreDeserializer(serializers.Serializer):
    id = serializers.UUIDField(required=True)
    name = serializers.CharField(required=True, max_length=255)
    is_active = serializers.BooleanField(required=True)
    categories = SetField(child=serializers.UUIDField())
