import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from config_manager import default_config, server_config


def test_default_config_has_web_port():
    assert default_config.port is not None


def test_server_config_has_socket_host_and_port():
    assert server_config.host == '127.0.0.1'
    assert server_config.port == '9999'


def test_web_port_and_socket_port_do_not_collide():
    assert default_config.port != server_config.port
