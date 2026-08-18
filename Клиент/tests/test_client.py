import os
import sys

import tlv8

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from LanternClient import Client


def make_client():
    return Client('127.0.0.1', 9999)


def test_decode_command_recognizes_every_known_command():
    client = make_client()
    for command_name, meta in client.commands.items():
        length = int(meta['length'])
        buffer = tlv8.Entry(
            type_id=int(meta['type'], 16),
            data=bytes(length),
            data_type=tlv8.DataType.BYTES,
        ).encode()

        assert client.decode_command(buffer) == [command_name]


def test_decode_command_ignores_unknown_type():
    client = make_client()
    buffer = tlv8.Entry(type_id=0x7f, data=b'', data_type=tlv8.DataType.BYTES).encode()

    assert client.decode_command(buffer) == []
