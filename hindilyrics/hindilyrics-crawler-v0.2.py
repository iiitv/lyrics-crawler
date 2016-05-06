"""
{
    'initial' : xx
}
"""

import json
from getopt import getopt, GetoptError
from math import ceil
from os import path, mkdir
from queue import Queue
from re import findall, DOTALL
from time import strptime
from urllib import request

from print_util import print_info, current_time, print_error, print_usage, \
    print_warning

task_queue = Queue()  # She will do all the magic
location = ''
start_address = 'http://www.hindilyrics.net'
USAGE = 'python hindilyrics-crawler-v0.2.py -t <type of crawl DEFAULT : full>' \
        ' -n <number of threads DEFAULT : 4> -o <output destination DEFAULT :' \
        ' ./>'


def download_movie(init, url, movie):
    global location, start_address

    website = start_address + url
    raw_html = str(request.urlopen(website).read())

    movie_json = {
        'movie_name': movie,
        'website_prefix': 'http://www.hindilyrics.net',
        'movie_url': url
    }  # Create a json to dump in file

    songs_with_url = findall(r'<li>.*?\"(.*?)\">(.*?)<', raw_html)
    song_json_list = []  # List of songs with attributes

    for url_, song in songs_with_url:
        song_json = {
            'song_name': song,
            'song_url': url_
        }

        website_ = start_address + url_
        raw_html_ = str(request.urlopen(website_).read())

        # Get singers and all
        singers = findall(r'Singer\(s\).*?:(.*?)<br>', raw_html_)
        music_by = findall(r'Music By.*?:(.*?)<br>', raw_html_)
        lyricists = findall(r'Lyricist.*?:(.*?)<br>', raw_html_)

        singers_list = []
        if len(singers) > 0:  # If there are any
            singers = singers[0]  # Get the one of one
            singers = singers.split(', ')  # Split different singers
            for singer in singers:
                if singer.count('<a') != 0:
                    # The've got an page for him/her! Cool..
                    singer_url, singer_name = \
                        findall(r'<a.*?\"(.*?)\">(.*?)<', singer)[0]
                    # TODO - Get details of singer and save it in some
                    # directory. Maybe location/artists/name.json
                else:
                    singer_url = ''
                    singer_name = singer
                singer_dict = {
                    'singer_name': singer_name,
                    'singer_url': singer_url
                }
                singers_list.append(singer_dict)  # Put him in the list
        song_json['singers'] = singers_list  # Add it to song's json

        # Repeat same as above
        music_by_list = []
        if len(music_by) > 0:
            music_by = music_by[0]
            music_by = music_by.split(', ')
            for artist in music_by:

                if artist.count('<a') != 0:
                    artist_url, artist_name = \
                        findall(r'<a.*?\"(.*?)\">(.*?)<', artist)[0]
                else:
                    artist_url = ''
                    artist_name = artist

                artist_dict = {
                    'artist_name': artist_name,
                    'artist_url': artist_url
                }
                music_by_list.append(artist_dict)
        song_json['music_by'] = music_by_list

        # Repeat same as above
        lyricist_list = []
        if len(lyricists) > 0:
            lyricists = lyricists[0]
            lyricists = lyricists.split(', ')
            for lyricist in lyricists:
                if lyricist.count('<a') != 0:
                    lyricist_url, lyricist_name = \
                        findall(r'<a.*?\"(.*?)\">(.*?)<', lyricist)[0]
                else:
                    lyricist_url = ''
                    lyricist_name = lyricist

                lyricist_dict = {
                    'lyricist_name': lyricist_name,
                    'lyricist_url': lyricist_url
                }
                lyricist_list.append(lyricist_dict)
        song_json['lyricists'] = lyricist_list

        lyrics = findall(r'<font face="verdana\">(.*?)</font', raw_html_,
                         DOTALL)  # Finally!!
        song_json['lyrics'] = lyrics

        song_json_list.append(song_json)

    movie_json['songs'] = song_json_list
    movie_json['last_crawled'] = current_time()

    filename = location + '{0}/'.format(init) + movie + '.json'
    with open(filename, 'wb') as f:
        json.dump(movie_json, f)


def download_movies_from_page(init, number):
    global start_address, location

    website = start_address + '/lyrics/hindi-songs-starting-{0}-page-{1}.html' \
        .format(init, number)
    raw_html = str(request.urlopen(website).read())

    # Fetch movies and their URL
    movies_list_with_url = findall(r'<li>.*?\"(.*?)\">(.*?)<', raw_html)

    for url, movie in movies_list_with_url:

        # Sort of normalization, shall work
        movie = movie.replace('/', '_').replace('-', '_').replace(':', '_')
        file_name = location + '{0}/{1}.json'.format(init, movie)

        fetch = False

        if path.exists(file_name):  # If file is there
            with open(file_name) as f:
                movie_json = json.load(f)
            time_format = '%Y-%m-%d %H:%M:%S'
            # How many seconds before was it crawled
            second_gap = (strptime(current_time(), time_format) -
                          strptime(movie_json['last_crawled'],
                                   time_format)).seconds
            # 3 hrs < gap < 5 months - Cuz if its older, they won't update
            # (probably)
            if 10800 < second_gap < 12960000:
                fetch = True
        else:  # Never heard of it, let's go
            fetch = True

        if fetch:
            download_movie(init, url, movie)


def initial(init):
    global start_address

    website = start_address + '/lyrics/hindi-songs-starting-{0}-page-1.html' \
        .format(init)

    raw_html = str(request.urlopen(website).read())

    path_init = location + init
    if not path.isdir(path_init):  # If folder doesn't exists
        mkdir(path_init)  # Make it exist

    if initial != '0':  # If not zero, it will be at this position
        number_of_movies = raw_html[2343:].split(" ", 1)[0]
    else:  # Else count list elements, buggy site
        number_of_movies = raw_html.count('<li>')

    number_of_movies = int(number_of_movies)
    print_info('Found {0} movies starting with {1}.'.format(number_of_movies,
                                                            init))

    number_of_pages = ceil(number_of_movies / 90.0)  # They keep 90 per page

    for i in range(1, number_of_pages + 1):
        download_movies_from_page(init, i)


def threader():
    while not task_queue.empty():
        init = task_queue.get()  # Take out something from the queue
        initial(init)


def process_arguments(arguments):
    global USAGE, location

    try:
        opts, args = getopt(
            arguments,
            't:n:o:',
            [
                'type=',
                'number-of-threads=',
                'output-location='
            ]
        )
    except GetoptError:
        print_error('Invalid arguments')
        print_usage(USAGE)
        import sys
        sys.exit()

    number_of_threads = 4
    location = './'
    crawl_type = 'full'
    for opt, arg in opts:
        if opt in ('-t', '--type'):
            if arg not in ('full', 'incr'):
                print_warning('Crawl type not recognized, using default')
            else:
                crawl_type = arg
        elif opt in ('-n', '--number-of-threads'):
            number_of_threads = int(arg)
        elif opt in ('-o', '--output-location'):
            if arg[-1] != '/':
                arg += '/'
            location = arg

    return number_of_threads, crawl_type


def main():
    import sys
    process_arguments(sys.argv[1:])
