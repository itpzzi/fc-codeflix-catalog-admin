from dataclasses import dataclass

from src.core._shared.domain.entity import EntityNamed


@dataclass(eq=False)
class Category(EntityNamed):
    description: str = ""
    is_active: bool = True

    def validate(self):
        self._validate_name(self.name)
        self._check_notification_has_errors()

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
