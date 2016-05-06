# TODO - Add connection error handling
# TODO - Add keyboard interrupt management

import json
import math
import string
import sys
from datetime import datetime
from os import path, mkdir
from re import findall, DOTALL
from threading import Thread
from time import sleep
from time import time, strptime
from urllib import request

usage = "python hindilyrics-crawler <crawl type - full/incr> <destination>"
start_address = 'http://www.hindilyrics.net'
location = ''


def current_time():  # Get current time
    return datetime.fromtimestamp(time()).strftime('%Y-%m-%d %H:%M:%S')


def print_info(level, message):  # Information printing utility
    message = '(' + current_time() + ') INFO: ' + message
    for i in range(0, level):
        message = '\t' + message
    print(message)


def download_movie(level, init, url, movie):
    sleep(0.001)
    global location, start_address

    print_info(level, 'Started thread for downloading movie {0}.'.format(movie))

    website = start_address + url
    raw_html = str(request.urlopen(website).read())

    movie_json = {
        'movie_name': movie,
        'website_prefix': 'http://www.hindilyrics.net',
        'movie_url': url
    }  # Create a json to dump in file

    songs_with_url = findall(r'\<li\>.*?\"(.*?)\"\>(.*?)\<', raw_html)
    song_json_list = []  # List of songs with attributes

    for url_, song in songs_with_url:
        song_json = {
            'song_name': song,
            'song_url': url_
        }

        website_ = start_address + url_
        raw_html_ = str(request.urlopen(website_).read())

        # Get singers and all
        singers = findall(r'Singer\(s\).*?:(.*?)\<br\>', raw_html_)
        music_by = findall(r'Music\ By.*?:(.*?)\<br\>', raw_html_)
        lyricists = findall(r'Lyricist.*?:(.*?)\<br\>', raw_html_)

        singers_list = []
        if len(singers) > 0:  # If there are any
            singers = singers[0]  # Get the one of one
            singers = singers.split(', ')  # Split different singers
            for singer in singers:
                if singer.count('<a') != 0:  # The've got an page for him/her! Cool..
                    singer_url, singer_name = findall(r'\<a.*?\"(.*?)\"\>(.*?)\<', singer)[0]
                    # TODO - Get details of singer and save it in some directory. Maybe location/artists/name.json
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
                    artist_url, artist_name = findall(r'\<a.*?\"(.*?)\"\>(.*?)\<', artist)[0]
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
                    lyricist_url, lyricist_name = findall(r'\<a.*?\"(.*?)\"\>(.*?)\<', lyricist)[0]
                else:
                    lyricist_url = ''
                    lyricist_name = lyricist

                lyricist_dict = {
                    'lyricist_name': lyricist_name,
                    'lyricist_url': lyricist_url
                }
                lyricist_list.append(lyricist_dict)
        song_json['lyricists'] = lyricist_list

        lyrics = findall(r'\<font face="verdana\"\>(.*?)\</font', raw_html_, DOTALL)  # Finally!!
        song_json['lyrics'] = lyrics

        song_json_list.append(song_json)

    movie_json['songs'] = song_json_list
    movie_json['last_crawled'] = current_time()

    filename = location + movie + '.json'
    with open(filename, 'wb') as f:
        json.dump(movie_json, f)


def download_movies_from_page(level, init, number):
    sleep(0.001)
    global start_address, location
    print_info(level, 'Started thread for downloading movies starting with {0} page {1}'.format(init, number))

    website = start_address + '/lyrics/hindi-songs-starting-{0}-page-{1}.html'.format(init, number)
    raw_html = str(request.urlopen(website).read())

    movies_list_with_url = findall(r'\<li\>.*?\"(.*?)\"\>(.*?)\<', raw_html)  # Fetch movies and their URL

    for url, movie in movies_list_with_url:

        movie = movie.replace('/', '_').replace('-', '_').replace(':', '_')  # Sort of normalization, shall work
        file_name = location + '{0}/{1}.json'.format(init, movie)

        fetch = False

        if path.exists(file_name):  # If file is there
            with open(file_name) as f:
                movie_json = json.load(f)
            time_format = '%Y-%m-%d %H:%M:%S'
            second_gap = (strptime(current_time(), time_format) - strptime(movie_json['last_crawled'], time_format)) \
                .seconds  # How many seconds before was it crawled
            if 10800 < second_gap < 12960000:  # 3 hrs < gap < 5 months - Cuz if its older, they won't update (probably)
                fetch = True
        else:  # Never heard of it, let's go
            fetch = True

        if fetch:  # Just get it, no need to wait for completion (probably)
            thread_for_movie = Thread(target=download_movie, args=(level + 1, init, url, movie))
            thread_for_movie.start()


def initial(level, init):
    sleep(0.001)
    global start_address
    print_info(level, 'Started thread for downloading metadata for movies starting with {0}'.format(init))
    website = start_address + '/lyrics/hindi-songs-starting-{0}-page-1.html'.format(init)

    raw_html = str(request.urlopen(website).read())

    path_init = location + init
    if not path.isdir(path_init):  # If folder doesn't exists
        mkdir(path_init)  # Make it exist

    if initial != '0':  # If not zero, it will be at this position
        number_of_movies = raw_html[2343:].split(" ", 1)[0]
    else:  # Else count list elements, buggy site
        number_of_movies = raw_html.count('<li>')

    number_of_movies = int(number_of_movies)
    print_info(level, 'Found {0} movies starting with {1}.'.format(number_of_movies, init))

    number_of_pages = math.ceil(number_of_movies / 90.0)  # They keep 90 per page

    threads = {}  # Thread keeping dict
    for i in range(1, number_of_pages + 1):
        threads[i] = Thread(target=download_movies_from_page, args=(level + 1, init, i))
        threads[i].start()


def full_crawl(level=0):
    sleep(0.001)
    initials = ['0', ] + list(string.ascii_lowercase[:])  # All lowercase things

    while True:  # Forever (until user preempts)
        print_info(level, 'Starting full crawl')
        thread_dict = {}  # To keep all the thread objects

        for init in initials:  # For every thing possible
            thread_dict[init] = Thread(target=initial, args=(level + 1, init))
            thread_dict[init].start()

        for init in initials:  # Wait for every one to complete
            thread_dict[init].join()


def incremental_crawl():
    pass


def main():
    global location
    if len(sys.argv) != 3:
        print(usage)
        raise ValueError('Expected {0} arguments recieved {1}.'.format(3, len(sys.argv)))

    # Expecting user to input some good location
    crawl_type = sys.argv[1]

    # Some bad argument
    if crawl_type not in ('full', 'incr'):
        raise ValueError('Invalid crawl type')

    location = sys.argv[2]
    # Append '/' at the end of location if not already there
    if location[-1] != '/':
        location += '/'
    if not path.isdir(location):
        mkdir(location)

    if crawl_type == 'full':
        full_crawl(0)  # Look for all pages repeatedly, needed only at first go
    else:
        incremental_crawl()  # Look only fir the updated songs / New albums


if __name__ == "__main__":
    main()
