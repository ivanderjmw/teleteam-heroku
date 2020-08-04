release: python manage.py migrate
web: python manage.py botpolling --username=teleteam_bot
web: gunicorn teleteam.wsgi --log-file -