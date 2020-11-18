#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio

import websockets
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from starlette.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocket

from simulator import celery_app
from simulator.core import states
from simulator.api.api_v1.api import api_router
from simulator.core import handlers
from simulator.core.states import TaskStatusEnum
from simulator.settings.config import settings


def create_app(**kwargs) -> FastAPI:
    application = FastAPI(**kwargs)
    register_event_handler(application)
    register_error_handler(application)
    register_middleware(application)
    register_router(application)
    return application


def register_event_handler(application: FastAPI):
    application.add_event_handler('startup', handlers.startup_event)
    application.add_event_handler('shutdown', handlers.shutdown_event)


def register_error_handler(application: FastAPI):
    application.add_exception_handler(HTTPException, handlers.http_error_handler)
    application.add_exception_handler(RequestValidationError,
                                      handlers.http422_error_handler)


def register_middleware(application: FastAPI):
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],

    )


def register_router(application: FastAPI):
    application.include_router(api_router, prefix=settings.API_V1_STR)


app = create_app()


@app.websocket('/{task_id}')
async def get_task_state(
        task_id: str,
        websocket: WebSocket
):
    await websocket.accept()

    while True:
        async_result = celery_app.AsyncResult(task_id)
        state = TaskStatusEnum.__members__[async_result.status].value
        if state in [TaskStatusEnum.PROGRESS, TaskStatusEnum.PAUSE]:
            result = {
                'state': state,
                'progress': async_result.result['progress'] * 100,
                'result': async_result.result['result']
            }
        elif state == TaskStatusEnum.FAILURE:
            result = {
                'state': state,
                'traceback': async_result.traceback
            }
        elif state == TaskStatusEnum.SUCCESS:
            result = {
                'state': state,
                'progress': 100,
                'result': async_result.result['result']
            }
        else:
            result = {
                'state': state,
            }

        try:
            await websocket.send_json(result)
        except websockets.ConnectionClosedError:
            await websocket.close()
            break
        await asyncio.sleep(2)
