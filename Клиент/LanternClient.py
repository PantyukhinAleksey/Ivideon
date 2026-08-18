import asyncio
import json
import os
import socket
from asyncio import AbstractEventLoop

import tlv8
from aiohttp import web
from aiohttp.web_app import Application

from config_manager import default_config, server_config
from logger import AppLogger

LOG_PATH = os.path.join(os.path.dirname(__file__), 'client.log')
logger = AppLogger('lantern.client', LOG_PATH).get()

COMMANDS_PATH = os.path.join(os.path.dirname(__file__), 'commands')


class Client:

    def __init__(self, server_host, server_port):
        self.server_host = server_host
        self.server_port = int(server_port)
        self.client = None
        self.commands = self.read_commands()

    async def connect(self, loop):
        while True:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setblocking(False)
            try:
                await loop.sock_connect(sock, (self.server_host, self.server_port))
                self.client = sock
                logger.info('Подключились к серверу %s:%s', self.server_host, self.server_port)
                return
            except OSError as ex:
                logger.warning('Не удалось подключиться к серверу: %s', ex)
                sock.close()
                await asyncio.sleep(5)

    async def start_worker(self, loop: AbstractEventLoop):
        while True:
            if self.client is None:
                await self.connect(loop)
            try:
                data = await loop.sock_recv(self.client, 4096)
                if not data:
                    raise ConnectionError('Сервер закрыл соединение')
            except OSError as ex:
                logger.warning('Соединение с сервером потеряно: %s', ex)
                self.client.close()
                self.client = None
                continue

            values = self.decode_command(data)
            for value in values:
                logger.info('Получили команду от сервера: %s', value)
                match value:
                    case 'ON':
                        logger.info('Светим и освещаем путь.')

                    case 'OFF':
                        logger.info('Выключаемся.')

                    case 'COLOR':
                        logger.info('Меняем цвет.')

                    case _:
                        logger.info('Странная команда, ничего не делаем.')

    @staticmethod
    def read_commands():
        with open(COMMANDS_PATH) as file:
            return json.loads(file.read())

    def decode_command(self, value):
        values = []
        entries = tlv8.decode(value)
        for entry in entries:
            length = len(entry.data)
            commands = [
                x for x, y in self.commands.items()
                if int(y.get('type'), 16) == entry.type_id and int(y.get('length')) == length
            ]
            values.extend(commands)
        return values


def start_app(app: web.Application):
    io_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(io_loop)
    client = Client(server_config.host, server_config.port)
    io_loop.create_task(client.start_worker(io_loop))
    logger.info('Client started at port %s', default_config.port)
    web.run_app(app, port=int(default_config.port), loop=io_loop)


if __name__ == '__main__':
    app = Application(client_max_size=1073741824)
    start_app(app)
