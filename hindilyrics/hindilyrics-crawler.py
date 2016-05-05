import json
import math
import string
import sys
from datetime import datetime
from os import path, mkdir
from re import findall
from threading import Thread
from time import time, strptime
from urllib import request

usage = "python hindilyrics-crawler <crawl type - full/incr> <destination>"
start_address = 'http://www.hindilyrics.net'
location = ''


def current_time():
    return datetime.fromtimestamp(time()).strftime('%Y-%m-%d %H:%M:%S')


def print_info(level, message):
    message = '(' + current_time() + ') INFO: ' + message
    for i in range(0, level):
        message = '\t' + message
    print(message)


def download_movie(url):
    pass


def download_movies_from_page(level, init, number):
    global start_address, location
    print_info(level, 'Started thread for downloading movies starting with {0} page {1}'.format(init, number))

    website = start_address + '/lyrics/hindi-songs-starting-{0}-page-{1}.html'.format(init, number)
    raw_html = str(request.urlopen(website).read())

    movies_list_with_url = findall(r'\<li\>.*?\"(.*?)\"\>(.*?)\<', raw_html)

    for url, movie in movies_list_with_url:
        file_name = location + '{0}.json'.format(init)

        fetch = False

        if path.exists(file_name):
            with open(file_name) as f:
                movie_json = json.load(f)
            time_format = '%Y-%m-%d %H:%M:%S'
            second_gap = (
            strptime(current_time(), time_format) - strptime(movie_json['last_crawled'], time_format)).seconds
            if 10800 < second_gap < 12960000:
                fetch = True
        else:
            fetch = True

        if fetch:
            thread_for_movie = Thread(target=download_movie, args=(url, movie))
            thread_for_movie.start()


def initial(level, init):
    global start_address
    print_info(level, 'Started thread for downloading metadata for movies starting with {0}'.format(init))
    website = start_address + '/lyrics/hindi-songs-starting-{0}-page-1.html'.format(init)

    raw_html = str(request.urlopen(website).read())
    number_of_movies = raw_html.count('<li>')

    print_info(level, 'Found {0} movies starting with {1}.'.format(number_of_movies, init))

    number_of_pages = math.ceil(number_of_movies / 90.0)

    threads = {}
    for i in range(1, number_of_pages + 1):
        threads[i] = Thread(target=download_movies_from_page, args=(level + 1, init, i))
        threads[i].start()


def full_crawl(level=0):
    initials = ['0'] + string.ascii_lowercase

    while True:
        print_info(level, 'Starting full crawl')
        thread_dict = {}

        for init in initials:
            thread_dict[init] = Thread(target=initial, args=(level + 1, init))
            thread_dict[init].start()

        for init in initials:
            thread_dict[init].join()


def incremental_crawl():
    pass


def main():
    global location
    if len(sys.argv) != 3:
        print(usage)
        raise ValueError('Expected {0} arguments recieved {1}.'.format(3, len(sys.argv)))

    crawl_type = sys.argv[1]

    if crawl_type not in ('full', 'incr'):
        raise ValueError('Invalid crawl type')

    location = sys.argv[2]
    if location[-1] != '/':
        location += '/'
    if not path.isdir(location):
        mkdir(location)

    if crawl_type.matches('full'):
        full_crawl(0)
    else:
        incremental_crawl()


if __name__ == "__main__":
    main()
