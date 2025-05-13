from rest_framework import serializers


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
