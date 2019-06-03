#!/usr/bin/env bash
python manage.py migrate
python manage.py collectstatic --noinput --verbosity 0
gunicorn main.wsgi -w 4 -b 0.0.0.0:8000 --chdir=/app
