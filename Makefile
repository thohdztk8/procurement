.PHONY: up down build logs shell migrate seed restart

up:
	docker compose up -d

down:
	docker compose down

build:
	docker compose up --build -d

logs:
	docker compose logs -f web

shell:
	docker compose exec web python manage.py shell

migrate:
	docker compose exec web python manage.py migrate

seed:
	docker compose exec web python manage.py seed_roles

restart:
	docker compose restart web celery

ps:
	docker compose ps

clean:
	docker compose down -v --remove-orphans
