from django.contrib import admin

from src.django_project.category_app.models import Category


class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "description",
        "is_active",
        "created_at",
        "updated_at",
    )
    search_fields = ("name",)
    list_filter = ("is_active",)
    ordering = ("-created_at",)
    list_per_page = 20


admin.site.register(Category, CategoryAdmin)
