import asyncio
import json
import random

import tlv8
from aiohttp import web
from aiohttp.web import Application

from config_manager import default_config


class Socket:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client = None
        self.commands = self.read_commands()
        self.command_index = 0

    def connect(self):
        import socket
        server_address = (self.host, int(self.port))
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind(server_address)
            self.server.listen(1)
            print("Ждём подключения клиента...")
            self.client, a = self.server.accept()
        except:
            pass

    async def start_worker(self, loop):
        try:
            print(f'Send command')
            buffer = self.get_random_command()
            self.client.sendall(buffer)
        except:
            pass
        finally:
            await asyncio.sleep(10)
            await self.start_worker(loop)

    def get_random_command(self):
        self.command_index += 1
        command = random.choice(list(self.commands))
        return tlv8.Entry(type_id=self.command_index,
                          data=self.commands.get(command).get('type').encode('utf-8'),
                          data_type=tlv8.DataType.BYTES,
                          length=int(self.commands.get(command).get('length'))).encode()

    @staticmethod
    def read_commands():
        with open('commands') as file:
            return json.loads(file.read())


def start_app(app: web.Application):
    io_loop = asyncio.get_event_loop()
    server = Socket(default_config.host, int(default_config.port))
    server.connect()
    io_loop.create_task(server.start_worker(io_loop))
    print(f'Server started at host {server.host} and port {server.port}')
    web.run_app(app, port=int(default_config.port))


if __name__ == '__main__':
    server = Application(client_max_size=1073741824)
    start_app(server)
