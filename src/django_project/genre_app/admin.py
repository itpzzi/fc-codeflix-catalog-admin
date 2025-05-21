from django.contrib import admin

from src.django_project.genre_app.models import Genre as GenreModel


class GenreAdmin(admin.ModelAdmin):
    pass


admin.site.register(GenreModel, GenreAdmin)
