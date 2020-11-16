#!/bin/bash
cd ..
gunicorn -c docs/gunicorn_conf.py  simulator.app:app

celery multi start 1 -A simulator -c4  --logfile=log/celery/%p.log --pidfile=pids/celery/%p.pid