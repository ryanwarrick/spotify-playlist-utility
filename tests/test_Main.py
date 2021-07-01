import configparser
from unittest.mock import MagicMock
from unittest import mock

@mock.patch('configparser.open')
def test_load_config_parser(self, mockFileOpen: mock.MagicMock):
    # https://github.com/eclarke/argutils/blob/master/tests/test_export.py
    # https://github.com/shaarli/python-shaarli-client/blob/master/tests/test_config.py
    # https://github.com/eclarke/argutils/blob/master/tests/test_read.py
    # TODO: Learn about unit tests and build out test logic here
    # TODO: Once tests written, implement tox testing within project
    pass
