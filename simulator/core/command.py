#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from enum import Enum


class CommandType(str, Enum):
    STOP = 'STOP',
    PAUSE = 'PAUSE'
    RESUME = 'RESUME'
