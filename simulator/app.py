#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import FastAPI, HTTPException
from starlette.middleware.cors import CORSMiddleware

from simulator.api.api_v1.api import api_router
from simulator.core import handlers
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
    application.add_exception_handler(HTTPException, handlers.http422_error_handler)


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
