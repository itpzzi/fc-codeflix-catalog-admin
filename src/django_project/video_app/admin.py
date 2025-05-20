# Register your models here.
from django.contrib import admin

from src.django_project.video_app.models import (
    AudioVideoMedia as AudioVideoMediaModel,
)
from src.django_project.video_app.models import (
    Video as VideoModel,
)


class VideoAdmin(admin.ModelAdmin):
    pass


class AudioVideoMediaAdmin(admin.ModelAdmin):
    pass


admin.site.register(VideoModel, VideoAdmin)
admin.site.register(AudioVideoMediaModel, AudioVideoMediaAdmin)
