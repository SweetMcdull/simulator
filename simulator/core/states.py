#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from enum import IntEnum

from celery.states import PENDING, STARTED, SUCCESS, FAILURE, REVOKED, RETRY, IGNORED

STOP = 'STOP'
PAUSE = 'PAUSE'
PROGRESS = 'PROGRESS'


class TaskStatusEnum(IntEnum):
    UNSTARTED = 0
    PENDING = 1
    PROGRESS = 2
    SUCCESS = 3
    FAILURE = 4
    STOP = 5
    PAUSE = 6
