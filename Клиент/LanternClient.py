import asyncio
import json

import tlv8
from aiohttp import web
from asyncio import AbstractEventLoop

from aiohttp.web_app import Application

from config_manager import default_config, server_config


class Client:

    def __init__(self, server_host, server_port):
        self.server_host = server_host
        self.server_port = server_port
        self.client = None
        self.commands = self.read_commands()

    def connect(self):
        import socket
        server_address = (self.server_host, self.server_port)
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect(server_address)
        except Exception as ex:
            print(ex)

    async def start_worker(self, loop: AbstractEventLoop):
        data = self.client.recv(4096)
        values = self.decode_command(data)
        for value in values:
            print("Получили команду от сервера:", value)
            match value:
                case 'ON':
                    print('Светим и освещаем путь.')

                case 'OFF':
                    print('Выключаемся.')

                case 'COLOR':
                    print('Меняем цвет.')

                case _:
                    print('Странная команда, ничего не делаем.')

        await asyncio.sleep(10)
        await self.start_worker(loop)

    @staticmethod
    def read_commands():
        with open('commands') as file:
            return json.loads(file.read())

    def decode_command(self, value):
        values = []
        entries = tlv8.deep_decode(value)
        for entry in entries:
            type = entry.data.decode('utf-8')
            length = entry.length
            commands = [x for x, y in self.commands.items() if y.get('type') == type and y.get('length') == length]
            values.extend(commands)
        return values


def start_app(app: web.Application):
    io_loop = asyncio.get_event_loop()
    client = Client(server_config.host, int(server_config.port))
    client.connect()
    io_loop.create_task(client.start_worker(io_loop))
    print(f'Client started at port {default_config.port}')
    web.run_app(app, port=int(default_config.port))


if __name__ == '__main__':
    server = Application(client_max_size=1073741824)
    start_app(server)
