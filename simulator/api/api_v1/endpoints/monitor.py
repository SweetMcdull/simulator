#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import APIRouter

router = APIRouter()


@router.post('/inspect', summary='监控查询')
def monitor_inspect():
    pass
