"""Настройки админ-панели Django."""
from django.contrib import admin

from .models import Filmwork, Genre, GenreFilmwork, Person, PersonFilmwork


class GenreFilmworkInline(admin.TabularInline):
    """Inline-меню для выбора Жанров внутри Кинопроизведения."""

    model = GenreFilmwork


class PersonFilmworkInline(admin.TabularInline):
    """Inline-меню для выбора Участников внутри Кинопроизведения."""

    model = PersonFilmwork


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    """Создание админ-панели Жанров."""

    list_display = ("name", "description", "created", "modified")

    search_fields = ("name",)


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    """Создание админ-панели Участников."""

    list_display = ("full_name", "created", "modified")

    search_fields = ("full_name",)


@admin.register(Filmwork)
class FilmworkAdmin(admin.ModelAdmin):
    """Создание админ-панели Кинопроизведений."""

    inlines = (GenreFilmworkInline, PersonFilmworkInline)

    list_display = ("title", "type", "creation_date", "rating", "created", "modified")

    list_filter = ("type", "genres")

    search_fields = ("title",)
