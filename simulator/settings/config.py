#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

from pydantic import BaseSettings


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    # 最大并发任务
    MAX_TASKS_NUM: int = os.cpu_count()


settings = Settings()
