from app.core.settings import get_settings

# Debugging
reload = get_settings().GUNICORN_RELOAD

# Log
loglevel = get_settings().GUNICORN_LOG_LEVEL
accesslog = get_settings().GUNICORN_LOG_ACCESS
access_log_format = get_settings().GUNICORN_LOG_FORMAT
errorlog = get_settings().GUNICORN_LOG_ERROR

# Socket
bind = get_settings().GUNICORN_BIND

# Workers
workers = get_settings().GUNICORN_WORKERS
worker_class = get_settings().GUNICORN_WORKER_CLASS
threads = get_settings().GUNICORN_THREADS
keepalive = get_settings().GUNICORN_KEEPALIVE
