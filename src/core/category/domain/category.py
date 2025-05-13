from dataclasses import dataclass

from src.core._shared.entity import Entity


@dataclass(eq=False)
class Category(Entity):
    description: str = ""
    is_active: bool = True

    def validate(self):
        self._validate_name(self.name)

    def update_category(self, name, description):
        self.name = name
        self.description = description

        self.validate()

    def activate(self):
        self.is_active = True

        self.validate()

    def deactivate(self):
        self.is_active = False

        self.validate()

    def __repr__(self):
        return f"<Category {self.name} {self.id}>"

    def __str__(self):
        return f"{self.name} - {self.description} {self.is_active}"
