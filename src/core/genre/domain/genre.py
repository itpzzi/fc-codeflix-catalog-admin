from dataclasses import dataclass, field
from uuid import UUID

from src.core._shared.entity import Entity


@dataclass(eq=False)
class Genre(Entity):
    is_active: bool = True
    categories: set[UUID] = field(default_factory=set)

    def validate(self):
        self._validate_name(self.name)

    def change_name(self, name):
        self.name = name
        self.validate()

    def activate(self):
        self.is_active = True
        self.validate()

    def deactivate(self):
        self.is_active = False
        self.validate()

    def add_category(self, category_id: UUID):
        self.categories.add(category_id)
        self.validate()

    def remove_category(self, category_id: UUID):
        self.categories.remove(category_id)
        self.validate()

    def _validate_name(self, value: str):
        if not value:
            raise ValueError("name cannot be empty")
        if len(value) > 255:
            raise ValueError("name cannot be longer than 255 characters")

    def __repr__(self):
        return f"<Genre {self.name} {self.id}>"

    def __str__(self):
        return f"{self.name} - {self.is_active}"
