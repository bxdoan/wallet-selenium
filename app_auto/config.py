import os
import logging

from python_json_config import ConfigBuilder
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)
CODE_HOME = os.path.abspath(os.path.dirname(__file__) + '/..')
HOME_PACKAGE = os.path.abspath(os.path.dirname(__file__) + '/package')

TMP_FOLDER = '/tmp'
TMP_ZKSYNC = '/tmp/zksync'
HOME_TMP = f'{CODE_HOME}/tmp'
HOME_LOG = f'{CODE_HOME}/log'
list_make_dir = [
    HOME_TMP, HOME_LOG, TMP_ZKSYNC
]
for _dir in list_make_dir:
    os.makedirs(_dir, exist_ok=True)

ACC_PATH = os.environ.get('ACC_PATH')
ACC_SUI_PATH = os.environ.get('ACC_SUI_PATH')

try:
    ACC_PATH = os.path.join(os.path.dirname(__file__), os.pardir, os.environ.get('ACC_PATH'))
    ACC_SUI_PATH = os.path.join(os.path.dirname(__file__), os.pardir, os.environ.get('ACC_SUI_PATH'))
except Exception as e:
    print(f"{ACC_PATH=} and {ACC_SUI_PATH} Error: {e}")

ACC_SUI = ACC_SUI_PATH.split('/')[-1].replace('.csv', '')
DRIVER_PATH = "driver/chromedriver"
WAIT_TIME = os.environ.get('WAIT_TIME')
PASSWORD = os.environ.get('PASSWORD')

HEADLESS = os.environ.get('HEADLESS')


EMAIL = os.environ.get('EMAIL')
PASSWORD_EMAIL = os.environ.get('PASSWORD_EMAIL')
EMAILCLONE_PREFIX = os.environ.get('EMAILCLONE_PREFIX')


def get_config():
    # create config parser
    _builder = ConfigBuilder()

    # parse config
    config_file_path = os.environ.get('CONFIG_FILE_PATH')
    if not config_file_path:
        raise Exception(f'Invalid config file path [{config_file_path}]')

    if not os.path.exists(config_file_path):
        # append to project home path
        config_file_path = os.path.join(os.path.dirname(__file__), os.pardir, config_file_path)

    if not os.path.exists(config_file_path):
        raise Exception(f'Invalid config file path [{config_file_path}]')

    _config = _builder.parse_config(config_file_path)

    return _config


def get_logger(name):
    log = logging.getLogger(name)
    log.setLevel("DEBUG")

    # Create handlers
    c_handler = logging.StreamHandler()

    # Create formatters and add it to handlers
    # Configure the logger
    simple_format = logging.Formatter(
        "%(asctime)s [%(funcName)s() +%(lineno)d]: %(levelname)-8s %(message)s",
        datefmt="%b-%d %H:%M:%S%Z"
    )
    c_handler.setFormatter(simple_format)

    # Add handlers to the logger
    log.addHandler(c_handler)

    return log


# Use this variable for global project
logger = get_logger(__name__)
config = get_config()
