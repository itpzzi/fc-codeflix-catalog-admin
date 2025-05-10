from uuid import uuid4
from django.db import models

from src.core.cast_member.domain.cast_member import CastMemberType


class CastMember(models.Model):
    app_label = "cast_member_app"

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=255)
    type = models.CharField(
        max_length=20,
        choices=[(type.value, type.name) for type in CastMemberType],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "cast_member_app"
        db_table = "cast_member"
        ordering = ["name"]
        verbose_name = "Cast Member"
        verbose_name_plural = "Cast Members"

    def __str__(self):
        return self.name
