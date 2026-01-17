import multiprocessing
import os

# Binding
bind = f'0.0.0.0:{os.environ.get("PORT", "5000")}'

# Workers
# (2 * cores) + 1 is a standard recommendation
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'gevent'  # Better for I/O bound tasks like our API
timeout = 120
keepalive = 2

# Logging
accesslog = '-' # Log to stdout
errorlog = '-'  # Log to stderr
loglevel = 'info'

# Process name
proc_name = 'agridecision_backend'

# Performance
max_requests = 1000
max_requests_jitter = 50
