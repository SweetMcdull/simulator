#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse

import uvicorn

from simulator import __version__


def runserver(args):
    uvicorn.run(args.app, host=args.host, port=args.port, reload=args.reload)


def main():
    parser = argparse.ArgumentParser(description="This is script help")
    sub_parser = parser.add_subparsers(title='subcommands')
    parser.add_argument(
        "--version",
        "-V",
        action="version",
        version=f"simulator version: {__version__}",
        help="show the version",
    )

    runserver_parser = sub_parser.add_parser('runserver')
    runserver_parser.add_argument(
        '--app',
        '-A',
        default='app:app',
        type=str,
        help='FastAPI app'
    )
    runserver_parser.add_argument(
        '--host',
        '-H',
        default='127.0.0.1',
        type=str,
        help='Server host'
    )
    runserver_parser.add_argument(
        '--port',
        '-P',
        default=5000,
        type=int,
        help='Server port'
    )
    runserver_parser.add_argument(
        '--reload',
        '-R',
        default=True,
        type=bool,
        help='Server reload'
    )
    runserver_parser.set_defaults(func=runserver)
    parse_args = parser.parse_args()
    parse_args.func(parse_args)
