#!/bin/bash

# Collect static files (optional)
# python manage.py collectstatic --noinput

# Apply database migrations
python manage.py makemigrations accounts posts
python manage.py migrate

# Run the application
gunicorn Threads.wsgi:application --bind 0.0.0.0:$PORT
