# !/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import time
from datetime import datetime
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
from pymysql import MySQLError

from simulator import celery_app
from simulator.core.command import CommandType
from simulator.core.db import MysqlHelper
from simulator.core.states import TaskStatusEnum
from simulator.settings.celery_config import (
    back_server, db_host, db_name, db_password, db_port, db_user, watch_url,
    client_secret
)

logger = get_task_logger(__name__)


class BaseTask(celery.Task):
    def __init__(self):
        self.watcher = redis.from_url(url=watch_url).pubsub()

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        self.update_client_state(TaskStatusEnum.FAILURE, ended=True)

    def on_success(self, retval, task_id, args, kwargs):
        self.update_client_state(TaskStatusEnum.SUCCESS, ended=True)

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
                    self.update_state(state=StatusCode.STOP.value)
                    self.update_client_state(TaskStatusEnum.STOP)
                    raise Ignore()
                elif CommandType(command) == CommandType.PAUSE:
                    logger.info(f'{self.request.id}: 接受到*暂停*信息')
                    arithmetic.process.status = StatusCode.PAUSE
                    self.update_state(state=StatusCode.PAUSE.value)
                    self.update_client_state(TaskStatusEnum.PAUSE)
                elif CommandType(command) == CommandType.RESUME:
                    logger.info(f'{self.request.id}: 接受到*恢复*信息')
                    arithmetic.process.status = StatusCode.PROGRESS
                    self.update_state(state=StatusCode.PROGRESS.value)
                    self.update_client_state(TaskStatusEnum.PROGRESS)
                else:
                    raise ValueError(f'无效的命令:{command}')

    def update_progress(self, state, data):
        data["start_time"] = self.start_time.strftime('%Y-%m-%d %H:%M:%S')
        data["end_time"] = None
        data["cost_time"] = round((datetime.now() - self.start_time).total_seconds(), 3)
        self.update_state(state=state, meta=data)

    # def update_client_state(self, state):
    #     url = parse.urljoin(back_server, '/api/v1/simulate/update_state')
    #     headers = {"secret": client_secret}
    #     with httpx.Client(timeout=5) as client:
    #         try:
    #             r = client.post(url, headers=headers, json={
    #                 'task_id': self.request.id,
    #                 'state': state
    #             })
    #         except HTTPError as e:
    #             self.update_state(state=states.FAILURE, traceback=e.args)
    #             logger.error(f'{self.request.id} 请求更新状态接口失败 {e.args}')
    #             raise Ignore
    #
    # def save_client_result(self, result: dict):
    #     url = parse.urljoin(back_server, '/api/v1/simulate/save_result')
    #     headers = {"secret": client_secret}
    #     with httpx.Client(timeout=5) as client:
    #         try:
    #             client.post(url, json=result, headers=headers)
    #         except HTTPError as e:
    #             self.update_state(state=states.FAILURE, traceback=e.args)
    #             logger.error(f'{self.request.id} 请求保存结果接口失败 {e.args}')
    #             raise Ignore

    def update_client_state(self, state: TaskStatusEnum, started=False, ended=False):
        task_id = self.request.id
        db = MysqlHelper(host=db_host, port=db_port, user=db_user, password=db_password,
                         database=db_name)

        state_value = state.value
        args = [state_value, task_id]

        query = f"""
        update `schema` set status=%s where task_id=%s
        """

        with db.auto_commit():
            try:
                rowcount = db.execute(query=query, args=args)
            except MySQLError as e:
                logger.warning(f"{task_id} 更新状态失败")

    def save_client_result(self, result):
        task_id = self.request.id
        db = MysqlHelper(host=db_host, port=db_port, user=db_user, password=db_password,
                         database=db_name)
        query = "select * from `schema` where task_id=%s"
        args = [task_id]
        schema = db.query_one(query=query, args=args)
        if not schema:
            self.update_state(state=TaskStatusEnum.FAILURE.value,
                              traceback="保存失败，方案未找到")
            raise Ignore
        schema_id = schema["id"]

        query = """
        INSERT INTO 
        `schema_result` 
        (task_id,schema_id,model_id,variable_code,result) 
            values 
         (%s , %s ,%s, %s ,%s )
        """
        args = []
        for model_id, m_result in result.items():
            for code, var_result in m_result.items():
                args.append([
                    task_id,
                    schema_id,
                    model_id,
                    code,
                    str(list(map(lambda x: float(x), var_result)))
                ])
        with db.auto_commit():
            # 删除历史记录
            db.execute(query="DELETE from schema_result WHERE schema_id = %s",
                       args=[schema_id, ])
            # 更新启动时间、结束时间
            db.execute(
                query="update `schema` set start_time=%s,end_time=%s where task_id=%s",
                args=[self.start_time, self.end_time, task_id])
            # 保存结果
            rowcount = db.execute_many(query=query, args=args)

    def update_init_input(self, result):
        task_id = self.request.id
        db = MysqlHelper(host=db_host, port=db_port, user=db_user, password=db_password,
                         database=db_name)
        args = [task_id]
        query = """
        SELECT
        s.id,
        s.schema_id,
        s.`value`,
        s.user_value,
        s.steady_value,
        s.last_value,
        p.`value` AS default_value,
        p.model_id,
        t.type_id,
        t.`code`
        FROM
            schema_parameter s
            JOIN project_parameter p ON s.parameter_id = p.id
            JOIN parameter t ON p.parameter_id = t.id 
            JOIN `schema` ON `schema`.id= s.schema_id 
        WHERE
            `schema`.task_id = %s 
        AND t.type_id = 'B003'
        """
        input_data = db.query_all(query, args)

        query = """
        UPDATE schema_parameter SET `last_value`=%s WHERE `id`=%s
        """
        args = []
        for record in input_data:
            input_id = record["id"]
            model_id = record["model_id"]
            var_name = record["code"]
            model_data = result.get(model_id)
            if model_data:
                if model_data.get(var_name):
                    value = model_data.get(var_name)
                    args.append([float(value[-1]), input_id])
        with db.auto_commit():
            db.execute_many(query, args)


@celery_app.task(base=BaseTask, bind=True, name='simulate-task')
def simulate(self, params: dict, use_init=False):
    self.start_time = datetime.now()
    self.end_time = None
    task_id = self.request.id
    self.update_client_state(TaskStatusEnum.PROGRESS, started=True)
    self.register_subscribe()
    process_plus = ProcessPlus(data=params)
    process_plus.arithmetic.solve(monitor_fun=self.monitor,
                                  update_progress=self.update_progress)
    process_plus.arithmetic.save_result()
    self.end_time = datetime.now()

    current_result = process_plus.arithmetic.get_current_result()
    result = {
        'progress': 100,
        "start_time": self.start_time.strftime('%Y-%m-%d %H:%M:%S'),
        "end_time": self.end_time.strftime('%Y-%m-%d %H:%M:%S'),
        "cost_time": round((self.end_time - self.start_time).total_seconds(), 3),
        'result': current_result,
    }
    self.save_client_result(process_plus.arithmetic.result)

    if use_init:
        logger.info(f"{task_id}:更新方案初始浓度")
        self.update_init_input(process_plus.arithmetic.result)
    return result


@celery_app.task(bind=True, name='test-add')
def add(self, x, y):
    for i in range(30):
        print(i * '*')
        time.sleep(1)
    return x + y
