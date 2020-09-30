#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import APIRouter

from simulator import celery_app
from simulator.response import Success

router = APIRouter()


@router.post('/create', summary='创建仿真任务')
def create_simulate():
    result = celery_app.send_task(name='test-add', args=(10, 20))
    return Success(result=result.task_id)


@router.post('/control', summary='仿真任务控制')
def control_simulate():
    result = celery_app.control.inspect().registered()
    return Success(result=result)


@router.post('/{task_id}', summary='任务控制详情查询')
def control_simulate(task_id: str):
    return Success()
