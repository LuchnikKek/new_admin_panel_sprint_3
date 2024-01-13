admin:
	DJANGO_SUPERUSER_USERNAME=admin \
	DJANGO_SUPERUSER_PASSWORD=123123 \
	DJANGO_SUPERUSER_EMAIL=mail@mail.ru \
	python app/manage.py createsuperuser --noinput | true

up:
	docker compose up -d --build

down:
	docker compose down | true

shell-plus: up
	docker compose exec django python manage.py shell_plus --print-sql

swagger-up:
	docker run -d --rm -p 8080:8080 \
			   --name swagger \
			   -v ./openapi.yaml:/swagger.yaml \
			   -e SWAGGER_JSON=/swagger.yaml \
			   swaggerapi/swagger-ui

swagger-down:
	docker stop swagger | true

# -f [service] - выводит логи конкретного сервиса
logs:
	docker compose logs -f $s & true

elastic-create:
	docker run -d -p 9200:9200 \
			   --name=elastic \
			   -e "discovery.type=single-node" \
			   -e "xpack.security.enabled=false" \
   			   -e ES_JAVA_OPTS="-Xms200m -Xmx200m" \
   			   elasticsearch:8.6.2

elastic-up:
	docker container start elastic

elastic-down:
	docker stop elastic | true

all-up: up swagger-up elastic-up

all-down: down swagger-down elastic-down
