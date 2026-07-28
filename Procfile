release: python manage.py migrate --noinput
web: gunicorn api_fusion.wsgi:application --log-file -
