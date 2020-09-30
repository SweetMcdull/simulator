#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from celery import Celery

from simulator.settings import celery_config

celery_app = Celery('simulator')

celery_app.conf.update(
    timezone='Asia/Shanghai'
)

celery_app.config_from_object(celery_config)


@celery_app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
