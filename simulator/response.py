#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Any

from pydantic import BaseModel


class Response(BaseModel):
    code: str
    msg: str
    result: Any = None

    class Meta:
        orm = True


class Success(Response):
    code = '200'
    msg = '操作成功'


class Failure(Response):
    code = '400'
    msg = '失败'
    errmsg: Any = None
