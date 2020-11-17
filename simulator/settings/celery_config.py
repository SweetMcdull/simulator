#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

watch_url: str = 'redis://127.0.0.1:6379/2'
back_server: str = 'http://127.0.0.1:50001'

broker_url = 'redis://127.0.0.1:6379/1'
result_backend = 'redis://127.0.0.1:6379/2'

imports = ['simulator.core.tasks']
worker_concurrency = os.cpu_count()  # worker并发数，默认cpu核数

# 日志配置
worker_redirect_stdouts_level = 'INFO'
worker_task_log_format = (
    "[%(asctime)s: %(levelname)s/%(processName)s]"
    "[%(task_name)s(%(task_id)s)] %(message)s"
)
worker_log_format = "[%(asctime)s: %(levelname)s/%(processName)s] %(message)s"

client_secret = "F194tBv1Goeoa9dcD4RA9wR2eiMjBxNJI1H5uf7LHM8"

db_host = "127.0.0.1"
db_port = 3306
db_user = "prosee_dev"
db_password = "prosee_dev"
db_name = "prosee_web2"
