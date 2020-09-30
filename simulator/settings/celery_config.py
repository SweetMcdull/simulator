#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

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
