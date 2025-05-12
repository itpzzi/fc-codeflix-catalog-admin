from rest_framework import serializers

from core.cast_member.domain.cast_member import CastMemberType


class CastMemberTypeField(serializers.ChoiceField):
    def __init__(self, **kwargs):
        choices = [(type_.value, type_.name) for type_ in CastMemberType]
        super().__init__(choices=choices, **kwargs)


class CreateCastMemberRequestSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    type = serializers.ChoiceField(
        choices=[(type.value, type.name) for type in CastMemberType]
    )


class CreateCastMemberResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()


class CastMemberResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField(max_length=255)
    type = CastMemberTypeField()


class ListCastMemberResponseSerializer(serializers.Serializer):
    data = CastMemberResponseSerializer(many=True)


class DeleteCastMemberRequestSerializer(serializers.Serializer):
    id = serializers.UUIDField()


class UpdateCastMemberRequestSerializer(serializers.Serializer):
    id = serializers.UUIDField(required=True)
    name = serializers.CharField(required=True, max_length=255)
    type = CastMemberTypeField(required=True)
