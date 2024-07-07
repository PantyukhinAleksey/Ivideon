import configparser
import os
from configparser import NoSectionError


class Config(object):
    def __init__(self, section, parser):
        self.section = section
        self.parser = parser
        if section != 'DEFAULT' and section not in self.parser.sections():
            raise NoSectionError(section)

    def _get_param(self, param_name):
        return self.parser.get(self.section, param_name, fallback=None)


class DefaultConfig(Config):
    def __init__(self, section, parser):
        super().__init__(section, parser)
        self.host = self._get_param('host')
        self.port = self._get_param('port')


class ServerConfig(Config):
    def __init__(self, section, parser):
        super().__init__(section, parser)
        self.host = self._get_param('host')
        self.port = self._get_param('port')


_app_config_path = os.path.join(os.path.dirname(__file__), '', 'config.ini')
_parser = configparser.ConfigParser(allow_no_value=True)
_parser.optionxform = str
_parser.read(_app_config_path)

default_config = DefaultConfig('DEFAULT', _parser)
server_config = ServerConfig('SERVER', _parser)
