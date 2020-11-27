#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import time

import redis
from fastapi import APIRouter, Body

from simulator.core.manager import manager
from simulator.settings import celery_config
from simulator.response import Success
from simulator.schemas.command import ControlCommand

router = APIRouter()


@router.post('/create', summary='创建仿真任务')
def create_simulate(params: dict = Body(...)):
    task_id = manager.create_task('simulate-task', task_id=str(int(time.time() * 1000)),
                                  args=(params["simulate"],), kwargs=params["meta"])
    return Success(result=task_id)


@router.post('/control', summary='仿真任务控制')
def control_simulate(command: ControlCommand):
    data = json.dumps(command.dict())
    with redis.from_url(url=celery_config.watch_url) as conn:
        conn.publish(channel=command.task_id, message=data)
    return Success()


@router.post('/{task_id}', summary='任务控制详情查询')
def control_simulate(task_id: str):
    return Success()
