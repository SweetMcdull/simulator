#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Union

from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from starlette import status
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse

from simulator.response import Failure


async def startup_event() -> None:
    """
    启动事件处理函数.
    Args:

    Returns:

    """
    pass


async def shutdown_event() -> None:
    """
    关闭事件处理函数.
    Args:

    Returns:

    """
    pass


async def http_error_handler(_: Request, exc: HTTPException):
    status_code = status.HTTP_200_OK
    # status_code = exc.status_code
    return JSONResponse(Failure(msg=exc.detail).dict(), status_code=status_code)


async def http422_error_handler(_: Request,
                                exc: Union[
                                    RequestValidationError, ValidationError],
                                ) -> JSONResponse:
    status_code = status.HTTP_200_OK
    return JSONResponse(Failure(msg='参数校验错误', errmsg=exc.errors()).dict(),
                        status_code=status_code)
