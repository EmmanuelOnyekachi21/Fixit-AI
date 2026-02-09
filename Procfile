web: daphne -b 0.0.0.0 -p ${PORT:-8080} config.asgi:application
worker: celery -A config worker -l info
