web: gunicorn index:server --workers 4 --preload
worker-default: celery -A tasks worker --loglevel=info
worker-beat: celery -A tasks beat --loglevel=info


