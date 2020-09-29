#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class SimulateError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
