#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import APIRouter

router = APIRouter()


@router.post('/active_tasks', summary='运行中的任务')
def active_tasks():
    pass
