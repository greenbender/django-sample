import multiprocessing

wsgi_app = 'sample.wsgi:application'
umask = 0o007
#workers = min(multiprocessing.cpu_count() * 2 + 1, 8)
workers = 1
loglevel = 'debug'
errorlog = '-'
timeout = 300
max_requests = 500

# development only settings
reload = True
graceful_timeout = 0
