#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import APIRouter, Body

router = APIRouter()


@router.post('/revoke_task', summary='取消任务')
def revoke_task(task_id: str = Body(..., embed=True)):
    pass


@router.post('/terminate_task', summary='终止任务')
def terminate_task(task_id: str = Body(..., embed=True)):
    pass
