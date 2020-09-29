import uvicorn
import click


@click.group()
def execute_from_command_line():
    pass


@click.command()
@click.option('--app', '-A', required=True, type=str, help='the server')
@click.option('--host', '-H', type=str, default='127.0.0.1', help='server`s host')
@click.option('--port', '-P', type=int, default=5000, help='server` port')
@click.option('--reload', '-R', type=bool, default=False, help='reload or not')
def runserver(app, host, port, reload):
    uvicorn.run(app, host=host, port=port, reload=reload)


execute_from_command_line.add_command(runserver)
