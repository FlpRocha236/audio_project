web: python manage.py migrate && gunicorn audio_project.wsgi --bind 0.0.0.0:$PORT
worker: celery -A audio_project worker -l info --pool=solo