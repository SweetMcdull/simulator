# !/usr/bin/env python3
# -*- coding: utf-8 -*-
from simulator import celery_app


@celery_app.task(bind=True, name='test-add')
def add(self, x, y):
    return x + y
