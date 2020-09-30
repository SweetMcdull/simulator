#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Optional

from pydantic import BaseModel

from simulator.enums import CommandCode


class ControlCommand(BaseModel):
    task_id: str
    command: CommandCode
    params: Optional[dict] = {}
