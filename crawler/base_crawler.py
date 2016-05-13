from queue import Queue
from threading import Thread
from urllib import request

from crawler import db_operations
from crawler import print_util

dummy_header = {'User-Agent': 'Mozilla/5.0'}


class BaseCrawler:
    def __init__(self, name, start_url):
        self.name = name
        self.start_url = start_url
        db_operations.create()


class CrawlerType0(BaseCrawler):
    task_queue = Queue()

    def __init__(self, name, start_url, list_of_url, number_of_threads):
        super().__init__(name, start_url)
        self.url_list = list_of_url
        self.number_of_threads = number_of_threads

    def threader(self, thread_id):
        while True:
            task = self.task_queue.get()

            if task[0] == 0:
                self.get_movies(thread_id, task[1])
            elif task[0] == 1:
                self.download_movie(thread_id, task[1], task[2])

    def run(self):

        thread_dict = {}
        for n in range(1, self.number_of_threads + 1):
            temp_thread = Thread(target=self.threader, args=(n,))
            thread_dict[n] = temp_thread
            temp_thread.start()

        for url in self.url_list:
            self.task_queue.put((0, url))

    def download_movie(self, thread_id, url, movie):

        print_util.print_info('{0} -> Downloading movie {1} -> {2}'.format(
            thread_id, movie, url))

        if db_operations.is_old_movie(self.start_url, url):
            db_operations.update_last_crawl(self.start_url, url)
            return

        movie_website = self.start_url + url
        raw_html = ''
        req = request.Request(movie_website, headers=dummy_header)
        done = False
        while not done:
            try:
                raw_html = request.urlopen(req).read().decode('utf-8')
                done = True
            except Exception:
                print_util.print_error(
                    '{0} -> Error downloading {1}. Retrying.'.format(
                        thread_id,
                        movie_website
                    )
                )

        song_with_url = self.get_songs_with_url(raw_html)

        if db_operations.number_of_songs(self.start_url, url) == len(
                song_with_url):
            db_operations.update_last_crawl(self.start_url, url)
            return

        for song_url, song in song_with_url:
            song_html = ''
            song_url = self.start_url + song_url
            req = request.Request(song_url, headers=dummy_header)
            done = False
            while not done:
                try:
                    song_html = request.urlopen(req).read().decode('utf-8')
                    done = True
                except Exception:
                    print_util.print_error(
                        '{0} -> Error downloading {1}. Retrying.'.format(
                            thread_id,
                            song_html
                        )
                    )

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
        req = request.Request(website, headers=dummy_header)
        raw_html = ''
        done = False
        while not done:
            try:
                raw_html = request.urlopen(req).read().decode('utf-8')
                done = True
            except Exception:
                print_util.print_error('{0} -> Error downloading {1}. Retrying.'
                                       .format(thread_id, website))

        movies_with_url = self.get_movies_with_url(raw_html)

        for url, movie in movies_with_url:
            self.task_queue.put((1, url, movie))

    @staticmethod
    def get_movies_with_url(raw_html):
        # User overrides this method to get list of movies from raw html
        return [('foobar.com', 'Foo Bar')]

    @staticmethod
    def get_songs_with_url(raw_html):
        # User overrides this method to get list of songs from raw html
        return [('foobar.com', 'Foo Bar')]

    @staticmethod
    def get_song_details(raw_html):
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
