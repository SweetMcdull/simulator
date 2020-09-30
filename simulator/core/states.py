#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from celery.states import PENDING, STARTED, SUCCESS, FAILURE, REVOKED, RETRY, IGNORED

STOP = 'STOP'
PAUSE = 'PAUSE'
PROGRESS = 'PROGRESS'
