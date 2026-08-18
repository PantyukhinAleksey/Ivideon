import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from config_manager import default_config, server_config


def test_default_config_has_own_web_port():
    assert default_config.port == '9998'


def test_server_config_points_to_the_lantern_server():
    assert server_config.host == '127.0.0.1'
    assert server_config.port == '9999'
