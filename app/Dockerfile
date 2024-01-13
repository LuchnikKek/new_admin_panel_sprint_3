FROM python:3.10

WORKDIR /opt/app
RUN groupadd -r django && useradd -d /opt/app -r -g django django

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV UWSGI_PROCESSES 1
ENV UWSGI_THREADS 8
ENV UWSGI_HARAKIRI 240
ENV DJANGO_SETTINGS_MODULE 'config.settings'

COPY --chown=django:django requirements.txt requirements.txt
COPY --chown=django:django uwsgi/uwsgi.ini uwsgi.ini
COPY --chown=django:django entrypoint.sh entrypoint.sh

RUN  mkdir static \
     && mkdir media \
     && pip install --no-cache-dir --upgrade pip \
     && pip install --no-cache-dir -r requirements.txt

COPY --chown=django:django . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

USER django

ENTRYPOINT ["sh", "entrypoint.sh"]
