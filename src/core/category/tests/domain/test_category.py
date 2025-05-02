import pytest
from uuid import UUID
import uuid

from src.core.category.domain.category import Category


class TestCategory:
    def test_name_is_required(self):
        with pytest.raises(
            TypeError, match="missing 1 required positional argument: 'name'"
        ):
            Category()

    def test_name_must_have_less_than_255_characters(self):
        name = "a" * 256
        with pytest.raises(ValueError, match="name cannot be longer than 255"):
            Category(name=name)

    def test_category_must_be_created_with_id_as_uuid_by_default(self):
        new_category = Category(name="Test Category")
        assert isinstance(new_category.id, UUID)

    def test_create_category_with_default_values(self):
        new_category = Category(name="Test Category")

        assert isinstance(new_category.id, UUID)
        assert isinstance(new_category.name, str)
        assert (
            isinstance(new_category.description, str) and new_category.description == ""
        )
        assert (
            isinstance(new_category.is_active, bool) and new_category.is_active is True
        )

    def test_create_category_as_active_by_default(self):
        new_category = Category(name="Test Category")
        assert new_category.is_active is True

    def test_create_category_with_provided_values(self):
        novo_id = uuid.uuid4()
        new_category = Category(
            name="Filme", description="Muito legal", id=novo_id, is_active=False
        )
        assert new_category.name == "Filme"
        assert new_category.description == "Muito legal"
        assert new_category.id == novo_id
        assert new_category.is_active is False

    def test_cannot_create_category_with_empty_name(self):
        with pytest.raises(ValueError, match="name cannot be empty"):
            Category(name="")


class TestUpdateCategory:
    def test_update_category_with_name_and_description(self):
        category = Category(name="Filme", description="Um filme")

        new_name = "Movie"
        new_description = "A movie"

        category.update_category(new_name, new_description)

        assert category.name == "Movie"
        assert category.description == "A movie"

    def test_update_category_with_invalid_name_raises_exception(self):
        category = Category(name="Filme", description="Um filme")

        new_name = "a" * 256
        new_description = "A movie"

        with pytest.raises(ValueError, match="name cannot be longer than 255"):
            category.update_category(new_name, new_description)

    def test_cannot_update_category_with_empty_name(self):
        category = Category(name="Filme", description="Um filme")

        new_name = ""
        new_description = "A movie"

        with pytest.raises(ValueError, match="name cannot be empty"):
            category.update_category(new_name, new_description)


class TestActivate:
    def test_activate_inactive_category(self):
        category = Category(name="Filme", is_active=False)

        category.activate()

        assert category.is_active is True

    def test_activate_active_category(self):
        category = Category(name="Filme")

        category.activate()

        assert category.is_active is True


class TestDeactivate:
    def test_deactivate_active_category(self):
        category = Category(name="Filme")

        category.deactivate()

        assert category.is_active is False

    def test_deactivate_inactive_category(self):
        category = Category(name="Filme", is_active=False)

        category.deactivate()

        assert category.is_active is False


class TestEquality:
    def test_when_categories_have_same_id_they_are_equal(self):
        common_id = uuid.uuid4()

        category1 = Category(id=common_id, name="Filme1")
        category2 = Category(id=common_id, name="Filme2")

        assert category1 == category2

    def test_equality_different_classes(self):
        class Dummy:
            pass

        common_id = uuid.uuid4()
        category = Category(id=common_id, name="Filme1")
        dummy_category = Dummy()
        dummy_category.id = common_id

        assert category != dummy_category
