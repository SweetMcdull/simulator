# !/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import time
from urllib import parse

import celery
import httpx
import redis
from celery import states
from celery.exceptions import Ignore
from celery.utils.log import get_task_logger
from httpx import HTTPError
from modellibrary import ProcessPlus
from modellibrary.src.main.python.core.algorithm.process import StatusCode

from simulator import celery_app
from simulator.core.command import CommandType
from simulator.settings.celery_config import back_server, watch_url, client_secret

logger = get_task_logger(__name__)


class BaseTask(celery.Task):
    def __init__(self):
        self.watcher = redis.from_url(url=watch_url).pubsub()

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        self.update_client_state(states.FAILURE)

    def on_success(self, retval, task_id, args, kwargs):
        self.update_client_state(states.SUCCESS)

    def run(self, *args, **kwargs):
        raise NotImplementedError('Tasks must define the run method.')

    def register_subscribe(self):
        self.watcher.psubscribe([self.request.id])

    def monitor(self, arithmetic):
        response = self.watcher.get_message()

        if response:
            channel = response['channel']
            msg = response["data"]
            if isinstance(msg, bytes):
                logger.debug(f'接受到订阅信息:{channel} {msg}')
                msg = json.loads(response["data"].decode(encoding='utf8'))
                command = msg['command']
                params = msg['params']
                if CommandType(command) == CommandType.STOP:
                    logger.info(f'{self.request.id}: 接受到*终止*信息')
                    arithmetic.process.status = StatusCode.STOP
                    self.update_state(state=StatusCode.STOP)
                    self.update_client_state(StatusCode.STOP)
                    raise Ignore()
                elif CommandType(command) == CommandType.PAUSE:
                    logger.info(f'{self.request.id}: 接受到*暂停*信息')
                    arithmetic.process.status = StatusCode.PAUSE
                elif CommandType(command) == CommandType.RESUME:
                    arithmetic.process.status = StatusCode.PROGRESS
                    logger.info(f'{self.request.id}: 接受到*恢复*信息')
                else:
                    raise ValueError(f'无效的命令:{command}')

    def update_progress(self, state, data):
        self.update_state(state=state, meta=data)

    def update_client_state(self, state):
        url = parse.urljoin(back_server, '/api/v1/simulate/update_state')
        headers = {"secret": client_secret}
        with httpx.Client(timeout=5) as client:
            try:
                r = client.post(url, headers=headers, json={
                    'task_id': self.request.id,
                    'state': state
                })
            except HTTPError as e:
                self.update_state(state=states.FAILURE, traceback=e.args)
                logger.error(f'{self.request.id} 请求更新状态接口失败 {e.args}')
                raise Ignore

    def save_client_result(self, result: dict):
        url = parse.urljoin(back_server, '/api/v1/simulate/save_result')
        headers = {"secret": client_secret}
        with httpx.Client(timeout=5) as client:
            try:
                client.post(url, json=result, headers=headers)
            except HTTPError as e:
                self.update_state(state=states.FAILURE, traceback=e.args)
                logger.error(f'{self.request.id} 请求保存结果接口失败 {e.args}')
                raise Ignore


@celery_app.task(base=BaseTask, bind=True, name='simulate-task')
def simulate(self, params: dict):
    task_id = self.request.id
    self.update_client_state(states.STARTED)
    self.register_subscribe()
    process_plus = ProcessPlus(data=params)
    process_plus.arithmetic.solve(self.monitor, self.update_progress)
    process_plus.arithmetic.save_result()

    result = {
        'progress': 100,
        'result': process_plus.arithmetic.get_current_result(),
    }
    self.save_client_result({
        'task_id': task_id,
        'result': process_plus.arithmetic.result
    })
    return result


@celery_app.task(bind=True, name='test-add')
def add(self, x, y):
    for i in range(30):
        print(i * '*')
        time.sleep(1)
    return x + y
