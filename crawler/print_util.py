from datetime import datetime
from time import time


def current_time():  # Get current time
    return datetime.fromtimestamp(time()).strftime('%Y-%m-%d %H:%M:%S')


def print_info(message):  # Information printing utility
    pr(message, 'INF')


def print_error(message):
    pr(message, 'ERR')


def print_warning(message):
    pr(message, 'WAR')


def print_usage(message):
    pr(message, 'USG')


def pr(m1, m2):
    message = '(' + current_time() + ') ' + m2 + ': ' + m1
    print(message)
