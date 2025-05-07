from rest_framework import serializers


class CategoryResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField(max_length=255)
    description = serializers.CharField()
    is_active = serializers.BooleanField()


class ListCategoryResponseSerializer(serializers.Serializer):
    data = CategoryResponseSerializer(many=True)


class RetrieveCategoryRequestSerializer(serializers.Serializer):
    id = serializers.UUIDField()


class RetrieveCategoryResponseSerializer(serializers.Serializer):
    data = CategoryResponseSerializer(source="*")


class CreateCategoryRequestSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(
        max_length=255, required=False, allow_blank=True, allow_null=False
    )
    is_active = serializers.BooleanField(default=True)


class CreateCategoryResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()


class UpdateCategoryRequestSerializer(serializers.Serializer):
    id = serializers.UUIDField(required=True)
    name = serializers.CharField(required=True, max_length=255)
    description = serializers.CharField(
        required=True, allow_blank=True, allow_null=False
    )
    is_active = serializers.BooleanField(required=True)

    def validate(self, attrs):
        if self.partial and not any(
            f in attrs for f in ["name", "description", "is_active"]
        ):
            raise serializers.ValidationError(
                "At least one field must be provided for partial update."
            )
        return attrs


class DeleteCategoryRequestSerializer(serializers.Serializer):
    id = serializers.UUIDField(required=True)
