#!/bin/sh
set -e

echo "Waiting for PostgreSQL..."
until python -c "import psycopg2; psycopg2.connect(dbname='${DB_NAME:-tenders}', user='${DB_USER:-postgres}', password='${DB_PASSWORD}', host='${DB_HOST:-db}', port='${DB_PORT:-5432}').close(); print('PostgreSQL ready')"; do
  sleep 2
done

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec gunicorn tender_tracking.wsgi:application --bind 0.0.0.0:8000 --workers 3