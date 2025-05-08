from rest_framework import serializers


class SetField(serializers.ListField):
    def to_internal_value(self, data):
        return set(super().to_internal_value(data))

    def to_representation(self, data):
        return list(super().to_representation(data))


class GenreResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField(max_length=255)
    is_active = serializers.BooleanField()
    categories = serializers.ListField(child=serializers.UUIDField())


class ListGenreResponseSerializer(serializers.Serializer):
    data = GenreResponseSerializer(many=True)


class CreateGenreRequestSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    is_active = serializers.BooleanField()
    categories = SetField(child=serializers.UUIDField())


class CreateGenreResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()


class DeleteGenreRequestSerializer(serializers.Serializer):
    id = serializers.UUIDField()


class UpdateGenreRequestSerializer(serializers.Serializer):
    id = serializers.UUIDField(required=True)
    name = serializers.CharField(required=True, max_length=255)
    is_active = serializers.BooleanField(required=True)
    categories = SetField(child=serializers.UUIDField())
