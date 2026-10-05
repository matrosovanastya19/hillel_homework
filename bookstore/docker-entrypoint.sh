#!/bin/bash

echo "Применение миграций базы данных..."
python manage.py migrate

echo "Сбор статических файлов..."
python manage.py collectstatic --noinput

exec "$@"