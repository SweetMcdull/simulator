#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import APIRouter

from .endpoints import simulate

api_router = APIRouter()
api_router.include_router(simulate.router, prefix='/simulate', tags=['仿真管理'])
