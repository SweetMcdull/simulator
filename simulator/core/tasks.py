# !/usr/bin/env python3
# -*- coding: utf-8 -*-
import time

from simulator import celery_app


@celery_app.task(bind=True, name='test-add')
def add(self, x, y):
    for i in range(30):
        print(i*'*')
        time.sleep(1)
    return x + y
