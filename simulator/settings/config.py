#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pydantic import BaseSettings


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"


settings = Settings()
