#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import APIRouter

from simulator.core.manager import manager
from simulator.response import Success

router = APIRouter()


@router.post('/active_tasks', summary='运行中的任务')
def active_tasks():
    result = manager.active_tasks()
    return Success(result=result)
