import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class UUIDMixin(models.Model):
    """Абстрактный класс для моделей, использующих uuid в качестве идентификатора.

    Attributes:
        id: UUID идентификатор записи.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        """Класс метаинформации."""

        abstract = True


class TimeStampedMixin(models.Model):
    """Абстрактный класс для моделей, у которых нужно сохранять дату создания и дату изменения.

    Attributes:
        created: Дата создания записи.
        modified: Дата изменения записи.
    """

    created = models.DateTimeField(_("Created"), auto_now_add=True)
    modified = models.DateTimeField(_("Modified"), auto_now=True)

    class Meta:
        """Класс метаинформации."""

        abstract = True


class Genre(UUIDMixin, TimeStampedMixin):
    """Модель Жанра.

    Attributes:
        name: Название Жанра.
        description: Описание Жанра.
    """

    name = models.CharField(_("Name"), max_length=255)
    description = models.TextField(_("Description"), blank=True)

    class Meta:
        """Класс метаинформации."""

        indexes = [
            models.Index(fields=["name"], name="genre_name_idx"),
        ]
        db_table = 'content"."genre'
        verbose_name = _("Genre")
        verbose_name_plural = _("Genres")

    def __str__(self):
        return self.name

class Person(UUIDMixin, TimeStampedMixin):
    """Модель Участника.

    Attributes:
        full_name: Полное имя.
    """

    full_name = models.CharField(_("Fullname"), max_length=255)

    class Meta:
        """Класс метаинформации."""

        indexes = [
            models.Index(fields=["full_name"], name="person_full_name_idx"),
        ]
        db_table = 'content"."person'
        verbose_name = _("Person")
        verbose_name_plural = _("Persons")

    def __str__(self):
        return self.full_name


class FilmworkType(models.TextChoices):
    """Типы Кинопроизведений."""

    MOVIE = "movie", _("Movie")
    TV_SHOW = "tv_show", _("TV show")


class Filmwork(UUIDMixin, TimeStampedMixin):
    """Модель Кинопроизведения.

    Attributes:
        title: Строка, содержащая название.
        description: Строка, содержащая описание.
        creation_date: Date-like строка с датой выхода фильма в формате YYYY-MM-DD.
        rating: Число с плавающей точкой 0.0 <= rating <= 100.0
        type: Строка с типом кинопроизведения, получаемая choice из класса FilmworkType.
        certificate: Строка с сертификатом подлинности.
        file_path: Файл Кинопроизведения.
        genres: М2М поле к таблице связи между Фильмами и Жанрами.
        persons: М2М поле к таблице связи между Фильмами и Участниками.
    """

    title = models.CharField(_("Title"), max_length=255)
    description = models.TextField(_("Description"), blank=True)
    creation_date = models.DateField(_("Creation date"), blank=True)
    rating = models.FloatField(
        _("Rating"),
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )  # noqa: WPS221,E501 этот код я скопипастил из курса
    type = models.CharField(
        _("Type"), max_length=50, choices=FilmworkType.choices, blank=True
    )  # noqa: WPS221,E501 этот тоже
    certificate = models.TextField(_("Certificate"), blank=True)
    file_path = models.FileField(_("File"), blank=True, null=True, upload_to="movies/")
    genres = models.ManyToManyField(Genre, _("Genres"), through="GenreFilmwork")
    persons = models.ManyToManyField(Person, _("Persons"), through="PersonFilmwork")

    class Meta:
        """Класс метаинформации."""

        indexes = [
            models.Index(fields=["title"], name="film_work_title_idx"),
            models.Index(fields=["creation_date"], name="film_work_creation_date_idx"),
            models.Index(fields=["rating"], name="film_work_rating_idx"),
        ]
        db_table = 'content"."film_work'
        verbose_name = _("Filmwork")
        verbose_name_plural = _("Filmworks")

    def __str__(self):
        return self.title


class GenreFilmwork(UUIDMixin):
    """Связь между Кинопроизведениями и Жанрами.

    Attributes:
        film_work: UUID Кинопроизведения.
        genre: UUID Жанра.
        created: Дата создания записи.
    """

    film_work = models.ForeignKey('Filmwork', on_delete=models.CASCADE)
    genre = models.ForeignKey(
        'Genre', verbose_name=_('Genre'), on_delete=models.CASCADE
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Класс метаинформации."""

        unique_together = (('film_work', 'genre'),)
        verbose_name = _('Genre')
        verbose_name_plural = _('Genres')
        db_table = 'content"."genre_film_work'


class PersonFilmworkRole(models.TextChoices):
    """Роли Участников."""

    ACTOR = 'actor', _('Actor')
    WRITER = 'writer', _('Writer')
    DIRECTOR = 'director', _('Director')



class PersonFilmwork(UUIDMixin):
    """Связь между Кинопроизведениями и Участниками.

    Attributes:
        film_work: UUID Кинопроизведения.
        person: UUID Участника.
        role: Строка с ролью Участника в Кинопроизведении.
        created: Дата создания записи.
    """

    film_work = models.ForeignKey(
        'Filmwork', verbose_name=_('Filmwork'), on_delete=models.CASCADE
    )
    person = models.ForeignKey(
        'Person', verbose_name=_('Person'), on_delete=models.CASCADE
    )
    role = models.TextField(
        _('Role'), max_length=50, choices=PersonFilmworkRole.choices, blank=True
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Класс метаинформации."""

        unique_together = (('film_work', 'person', 'role'),)
        verbose_name = _('Person')
        verbose_name_plural = _('Filmwork participants')
        db_table = 'content"."person_film_work'
