import traceback
from queue import Queue
from threading import Thread
from urllib import request

import db_operations
import print_util

dummy_header = {'User-Agent': 'Mozilla/5.0'}


class BaseCrawler:
    def __init__(self, name, start_url):
        self.name = name
        self.start_url = start_url
        db_operations.create()


class CrawlerType0(BaseCrawler):
    def __init__(self, name, start_url, list_of_url, number_of_threads):
        super().__init__(name, start_url)
        self.url_list = list_of_url
        self.number_of_threads = number_of_threads
        self.task_queue = Queue()

    def threader(self, thread_id):
        while not self.task_queue.empty():
            task = self.task_queue.get()

            if task[0] == 0:
                self.get_movies(thread_id, task[1])
            elif task[0] == 1:
                self.download_movie(thread_id, task[1], task[2])

    def run(self):

        while True:

            print('\n\n\n\n\n--------------------Starting New Crawl with {'
                  '0}--------------------'.format(self.name))

            self.task_queue = Queue()

            for url in self.url_list:
                self.task_queue.put((0, url))

            thread_dict = {}
            for n in range(1, self.number_of_threads + 1):
                temp_thread = Thread(target=self.threader, args=(n,))
                thread_dict[n] = temp_thread
                temp_thread.start()
            for n in range(1, self.number_of_threads + 1):
                thread_dict[n].join()

    def download_movie(self, thread_id, url, movie):

        print_util.print_info('{0} -> Downloading movie {1} -> {2}'.format(
            thread_id, movie, url))

        if db_operations.is_old_movie(self.start_url, url):
            db_operations.update_last_crawl(self.start_url, url)
            print_util.print_info(
                '{0} -> Skipping movie {1}, too old or too new.'.format(
                    thread_id,
                    movie
                )
            )
            return

        movie_website = self.start_url + url
        success, raw_html = open_request(thread_id, movie_website)

        if not success:
            self.task_queue.put((1, url, movie))
            return

        song_with_url = self.get_songs_with_url(raw_html)

        if db_operations.number_of_songs(self.start_url, url) == len(
                song_with_url):
            db_operations.update_last_crawl(self.start_url, url)
            print_util.print_info('{0} -> Skipping movie {1}, no new '
                                  'songs.'.format(
                thread_id,
                movie
            ))
            return

        for song_url, song in song_with_url:
            song_html = ''
            song_url_ = self.start_url + song_url
            success, song_html = open_request(thread_id, song_url_)

            if not success:
                self.task_queue.put((1, url, movie))
                return

            lyrics, singers, music_by, lyricist = self.get_song_details(
                song_html)

            new_id = db_operations.save(
                song=song,
                song_url=song_url,
                movie=movie,
                movie_url=url,
                start_url=self.start_url,
                lyrics=lyrics,
                singers=singers,
                director=music_by,
                lyricist=lyricist
            )

            print_util.print_info(
                '{0} -> Saved details of song {1} ({2}) with id {3}'.format(
                    thread_id,
                    song,
                    movie,
                    new_id
                )
            )

    def get_movies(self, thread_id, url):

        print_util.print_info('{0} -> Getting movies from page {1}.'.format(
            thread_id, url))

        website = self.start_url + url
        success, raw_html = open_request(thread_id, website)

        if not success:
            self.task_queue.put((0, url))
            return

        movies_with_url = self.get_movies_with_url(raw_html)

        print_util.print_info('{0} -> Found {1} movies on {2}'.format(
            thread_id,
            len(movies_with_url),
            url
        ))

        for url, movie in movies_with_url:
            self.task_queue.put((1, url, movie))

    def get_movies_with_url(self, raw_html):
        # User overrides this method to get list of movies from raw html
        return [('foobar.com', 'Foo Bar')]

    def get_songs_with_url(self, raw_html):
        # User overrides this method to get list of songs from raw html
        return [('foobar.com', 'Foo Bar')]

    def get_song_details(self, raw_html):
        # User overrides this method to get details for a song from raw html
        return (
            'lyrics',
            [
                'singer1',
                'singer2'
            ],
            'music director',
            'lyricist'
        )


class CrawlerType1(BaseCrawler):
    def __init__(self, name, start_url, list_of_url, number_of_threads):
        super().__init__(name, start_url)
        self.url_list = list_of_url
        self.number_of_threads = number_of_threads
        db_operations.create()
        self.task_queue = Queue()

    def run(self):

        thread_dict = {}
        for n in range(1, self.number_of_threads + 1):
            temp_thread = Thread(target=self.threader, args=(n,))
            thread_dict[n] = temp_thread
            temp_thread.start()

        while True:
            for url in self.url_list:
                self.task_queue.put((0, url))
            for n in range(1, self.number_of_threads + 1):
                thread_dict[n].join()

    def threader(self, thread_id):

        while not self.task_queue.empty():
            task = self.task_queue.get()

            if task[0] == 0:
                self.get_artists(thread_id, task[1])
            elif task[0] == 1:
                self.get_artist_albums(thread_id, task[1], task[2])

    def get_artists(self, thread_id, url):
        print_util.print_info(
            '{0} -> Getting artists from {1}'.format(
                thread_id,
                url
            )
        )

        website = self.start_url + url
        status, raw_html = open_request(thread_id, website)

        if not status:
            self.task_queue.put((0, url))
            return

        artists_with_url = self.get_artists_with_url(raw_html)

        print_util.print_info(
            '{0} -> Found {1} movies in {2}'.format(
                thread_id,
                len(artists_with_url),
                url
            )
        )

        for url, artist in artists_with_url:
            self.task_queue.put((1, url, artist))

    def get_artist_albums(self, thread_id, url, artist):

        print_util.print_info('{0} -> Getting albums for artist {1}'.format(
            thread_id,
            artist
        ))

        if db_operations.is_old_movie(
                self.start_url,
                url
        ):
            print_util.print_info(
                '{0} -> Skipping artist {1}, too old or too new.'.format(
                    thread_id,
                    artist
                )
            )

        website = self.start_url + url
        status, raw_html = open_request(thread_id, url)

        if not status:
            self.task_queue.put((1, url, artist))
            return

        albums_with_songs = self.get_albums_with_songs(raw_html)

        for album, song_with_url in albums_with_songs:
            for song_url, song in song_with_url:
                song_website = self.start_url + song_url
                success, song_html = open_request(thread_id, song_website)
                if not success:
                    self.task_queue.put((1, url, artist))
                    return

                lyrics = self.get_song_details(song_html)
                new_id = db_operations.save(
                    song=song,
                    song_url=song_url,
                    movie=album,
                    movie_url=url,
                    start_url=self.start_url,
                    lyrics=lyrics,
                    singers=artist,
                    director=artist,
                    lyricist=artist
                )

                print_util.print_info(
                    '{0} -> Saved song {1} ({2}) with ID {3}'.format(
                        thread_id,
                        song,
                        album,
                        new_id
                    )
                )

    def get_artists_with_url(self, raw_html):
        return [('a', 'a'), ]

    def get_albums_with_songs(self, raw_html):
        return [
            (
                'album1',
                [
                    ('url1', 'song1'),
                    ('url2', 'song2')
                ]
            ),
            (
                'album2',
                [
                    ('url3', 'song3'),
                    ('url4', 'song4')
                ]
            )
        ]

    def get_song_details(self, song_html):
        return 'la la la la'


def open_request(thread_id, url):
    url = url.replace('', '')
    req = request.Request(url, headers=dummy_header)
    try:
        raw_html = request.urlopen(req).read().decode('utf-8', 'ignore')
    except Exception as e:
        print_util.print_error(
            '{0} -> Error downloading {1}. Exception : {2}. '.format(
                thread_id,
                url,
                e
            )
        )
        traceback.print_exc()
        return False, ''
    return True, raw_html
