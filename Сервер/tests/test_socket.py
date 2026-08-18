import os
import sys

import tlv8

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from LanternServer import Socket


def make_socket():
    return Socket('127.0.0.1', 9999)


def test_get_random_command_encodes_type_and_length_for_every_command(monkeypatch):
    server = make_socket()
    for command_name, meta in server.commands.items():
        monkeypatch.setattr('random.choice', lambda choices, name=command_name: name)

        buffer = server.get_random_command()
        entries = tlv8.decode(buffer)

        assert len(entries) == 1
        assert entries[0].type_id == int(meta['type'], 16)
        assert len(entries[0].data) == int(meta['length'])


def test_command_index_increments():
    server = make_socket()
    assert server.command_index == 0
    server.get_random_command()
    server.get_random_command()
    assert server.command_index == 2
