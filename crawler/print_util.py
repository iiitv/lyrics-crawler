from datetime import datetime
from time import time


class Colors:
    RED = '\033[31m{0}\033[0m'
    GREEN = '\033[32m{0}\033[0m'
    ORANGE = '\033[33m{0}\033[0m'
    WHITE = '\033[0m{0}\033[0m'
    BLACK = '\033[30m{0}\033[0m'


def current_time():  # Get current time
    return datetime.fromtimestamp(time()).strftime('%Y-%m-%d %H:%M:%S.%f')


def print_info(message, color=Colors.WHITE):  # Information printing utility
    pr(message, 'INF', color)


def print_error(message, color=Colors.RED):
    pr(message, 'ERR', color)


def print_warning(message, color=Colors.ORANGE):
    pr(message, 'WAR', color)


def print_usage(message, color=Colors.WHITE):
    pr(message, 'USG', color)


def pr(m1, m2, color):
    message = '(' + current_time() + ') ' + m2 + ': ' + m1
    print(color.format(message))
