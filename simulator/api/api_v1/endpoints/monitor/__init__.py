#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import APIRouter

from . import inspect, control

router = APIRouter()
router.include_router(inspect.router, prefix='/inspect')
router.include_router(control.router, prefix='/control')
