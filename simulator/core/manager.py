#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime

from fastapi import HTTPException

from simulator import celery_app
from simulator.settings.config import settings


class Manager:
    def __init__(self):
        self.app = celery_app
        self.control = self.app.control
        self.inspect = self.control.inspect()

    @property
    def stats(self):
        return self.inspect.stats()

    def active_tasks(self):
        response = self.inspect.active()
        if not response:
            return {}
        for worker in response.keys():
            for tasks in response[worker]:
                tasks['time_start'] = datetime.datetime.fromtimestamp(
                    tasks['time_start']).strftime(
                    '%Y-%m-%d %H:%M:%S.%f')
        return response

    def create_task(self, task_name, task_id=None, args=None, kwargs=None):
        active_tasks = self.active_tasks()

        max_count = settings.MAX_TASKS_NUM
        current_task_count = sum([len(tasks) for _, tasks in active_tasks.items()])
        if current_task_count >= max_count:
            raise HTTPException(status_code=200,
                                detail=f"创建失败，超过最大任务数{max_count} 当前任务数:"
                                       f"{current_task_count}")

        result = self.app.send_task(name=task_name, task_id=task_id, args=args,
                                    kwargs=kwargs)
        return result.task_id


manager = Manager()
