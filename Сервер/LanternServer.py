import asyncio
import json
import os
import random
import socket

import tlv8
from aiohttp import web
from aiohttp.web import Application

from config_manager import default_config, server_config
from logger import AppLogger

LOG_PATH = os.path.join(os.path.dirname(__file__), 'server.log')
logger = AppLogger('lantern.server', LOG_PATH).get()

COMMANDS_PATH = os.path.join(os.path.dirname(__file__), 'commands')


class Socket:

    def __init__(self, host, port):
        self.host = host
        self.port = int(port)
        self.server = None
        self.client = None
        self.commands = self.read_commands()
        self.command_index = 0

    def listen(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host, self.port))
        self.server.listen(1)
        self.server.setblocking(False)

    async def accept_client(self, loop):
        while True:
            logger.info('Ждём подключения клиента...')
            try:
                self.client, address = await loop.sock_accept(self.server)
                self.client.setblocking(False)
                logger.info('Клиент подключился: %s', address)
                return
            except OSError as ex:
                logger.warning('Ошибка при приёме подключения: %s', ex)
                await asyncio.sleep(5)

    async def start_worker(self, loop):
        while True:
            if self.client is None:
                await self.accept_client(loop)
            try:
                buffer = self.get_random_command()
                await loop.sock_sendall(self.client, buffer)
            except OSError as ex:
                logger.warning('Клиент отключился: %s', ex)
                self.client.close()
                self.client = None
                continue
            await asyncio.sleep(10)

    def get_random_command(self):
        self.command_index += 1
        command = random.choice(list(self.commands))
        meta = self.commands[command]
        type_id = int(meta['type'], 16)
        length = int(meta['length'])
        payload = os.urandom(length) if length else b''
        logger.info('Команда #%d: %s', self.command_index, command)
        return tlv8.Entry(type_id=type_id, data=payload, data_type=tlv8.DataType.BYTES).encode()

    @staticmethod
    def read_commands():
        with open(COMMANDS_PATH) as file:
            return json.loads(file.read())


def start_app(app: web.Application):
    io_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(io_loop)
    server = Socket(server_config.host, server_config.port)
    server.listen()
    io_loop.create_task(server.start_worker(io_loop))
    logger.info('Server started at host %s and port %s', server.host, server.port)
    web.run_app(app, port=int(default_config.port), loop=io_loop)


if __name__ == '__main__':
    app = Application(client_max_size=1073741824)
    start_app(app)
