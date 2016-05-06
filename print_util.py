from datetime import datetime
from time import time


def current_time():  # Get current time
    return datetime.fromtimestamp(time()).strftime('%Y-%m-%d %H:%M:%S')


def print_info(message):  # Information printing utility
    message = '(' + current_time() + ') INF: ' + message
    print(message)


def print_error(message):
    message = '(' + current_time() + ') ERR: ' + message
    print(message)


def print_warning(message):
    message = '(' + current_time() + ') WAR: ' + message
    print(message)
