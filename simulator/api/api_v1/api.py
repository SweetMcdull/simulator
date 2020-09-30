#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import APIRouter

from .endpoints import simulate, monitor

api_router = APIRouter()
api_router.include_router(simulate.router, prefix='/simulate', tags=['仿真管理'])
api_router.include_router(monitor.router, prefix='/monitor', tags=['任务监控管理'])
