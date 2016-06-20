from queue import LifoQueue
from threading import Thread

import db_operations
import print_util
from network_manager import open_request
from print_util import colors


class BaseCrawler:
    def __init__(self, name, start_url, number_of_threads, max_err=10,
                 delay_request=False):
        """
        Base class for all other crawlers. This class contains all information
        that will be common in all crawlers.
        :param name: Name of crawler
        :param start_url: Base URL of website
        :param number_of_threads: Number of threads to use to crawl
        :param max_err: Max number of allowed errors for a crawl
        :param delay_request: Whether to delay while making requests or not
        """
        self.delay_request = delay_request
        self.name = name
        self.start_url = start_url
        self.number_of_threads = number_of_threads
        self.max_allowed_errors = max_err


class CrawlerType0(BaseCrawler):
    def __init__(self, name, start_url, list_of_url, number_of_threads,
                 max_err=10, delay_request=False):

        # Constructor for BaseCrawler
        """
        Crawler for the websites of type 0.
        :param list_of_url: List of URLs to start with.
        """
        super().__init__(name, start_url, number_of_threads, max_err,
                         delay_request)

        # Initialize data members
        self.task_queue = LifoQueue()
        self.url_list = list_of_url

    def threader(self, thread_id):
        """
        Worker function.
        :return:
        :param thread_id: Assigned ID of thread.
        """
        while not self.task_queue.empty():  # While there are any tasks

            task = self.task_queue.get()  # Get one of them

            if task['n_errors'] >= self.max_allowed_errors:  # Too many errors
                print_util.print_warning(
                    '{0} --> Too many errors in task {1}. Skipping.'.format(
                        thread_id,
                        task
                    )
                )
                continue

            print_util.print_info(
                '{0} --> New task : {1}'.format(
                    thread_id,
                    task
                )
            )  # Log the task

            try:

                # Call corresponding function
                if task['type'] == 0:
                    self.get_movies(
                        thread_id,
                        task['url']
                    )
                elif task['type'] == 1:
                    self.download_movie(
                        thread_id,
                        task['url'],
                        task['movie']
                    )
                elif task['type'] == 2:
                    self.download_song(
                        thread_id,
                        task['url'],
                        task['song'],
                        task['movie'],
                        task['movie_url']
                    )

                print_util.print_info(
                    'Task complete : {0}'.format(
                        task
                    ),
                    colors.GREEN
                )  # Log success

            except Exception as e:  # Some error
                print_util.print_error(
                    '{0} --> Error : {1}'.format(
                        thread_id,
                        e
                    )
                )  # Log it
                task['n_errors'] += 1  # Increment number of errors
                self.task_queue.put(task)  # Put back in queue

    def run(self):
        """
        Function to be called by subclasses to start crawler.
        """
        while True:
            # Crawl cycle start
            print_util.print_info(
                'Starting new crawl with {0}.'.format(
                    self.name
                )
            )
            # Add all URLs to task queue
            for url in self.url_list:
                self.task_queue.put(
                    {
                        'type': 0,
                        'url': url,
                        'n_errors': 0  # No errors initially
                    }
                )

            # Start all threads
            threads = []  # List for all threads
            for n in range(1, self.number_of_threads + 1):
                temp_thread = Thread(
                    target=self.threader,  # Worker function
                    args=(n,)  # Pass thread id as argument
                )
                threads.append(temp_thread)
                temp_thread.start()

            for temp_thread in threads:
                temp_thread.join()

                # Crawl cycle ends

    def download_movie(self, thread_id, url, movie):
        """
        Method to get all songs from a movie website.
        :param thread_id: As usual
        :param url: URL of movie
        :param movie: Name of movie
        """
        movie_website = self.start_url + url
        raw_html = open_request(movie_website, delayed=self.delay_request)

        song_with_url = self.get_songs_with_url(raw_html)

        # No new songs added
        if db_operations.number_of_songs(self.start_url, url) == len(
                song_with_url):
            db_operations.update_last_crawl(self.start_url, url)
            print_util.print_warning(
                '{0} --> Movie {1} contains no new songs. Skipping.'.format(
                    thread_id,
                    movie
                )
            )
            return

        # Add all songs
        for song_url, song in song_with_url:
            self.task_queue.put(
                {
                    'type': 2,
                    'url': song_url,
                    'song': song,
                    'movie': movie,
                    'movie_url': url,
                    'n_errors': 0
                }
            )

    def download_song(self, thread_id, url, song, movie, movie_url):
        """
        Method to get song details from website.
        :param thread_id: As usual
        :param url: URL of song
        :param song: Name of song
        :param movie: Name of movie
        :param movie_url: URL of movie
        """
        # Song already exists
        if db_operations.exists_song(self.start_url, url):
            print_util.print_warning(
                '{0} -> Song {1} already exists. Skipping.'.format(
                    thread_id,
                    song
                )
            )
            return

        # Get HTML
        song_url_ = self.start_url + url
        song_html = open_request(song_url_, delayed=self.delay_request)

        lyrics, singers, music_by, lyricist = self.get_song_details(song_html)

        # Save in database
        db_operations.save(
            song=song,
            song_url=url,
            movie=movie,
            movie_url=movie_url,
            start_url=self.start_url,
            lyrics=lyrics,
            singers=singers,
            director=music_by,
            lyricist=lyricist
        )

    def get_movies(self, thread_id, url):
        # Get website HTML
        """
        Get movie list from website
        :param thread_id: As usual
        :param url: URL of website from which movies are to be fetched
        """
        website = self.start_url + url
        raw_html = open_request(website, delayed=self.delay_request)

        # Add movies to task queue
        movies_with_url = self.get_movies_with_url(raw_html)
        for url, movie in movies_with_url:
            self.task_queue.put(
                {
                    'type': 1,
                    'url': url,
                    'movie': movie,
                    'n_errors': 0
                }
            )

    def get_movies_with_url(self, raw_html):
        # User overrides this method to get list of movies from raw html
        """
        Gets all movies' details from HTML code.
        :param raw_html: HTML code of web page
        :return: Movies with their URL
        """
        return [('foobar.com', 'Foo Bar')]

    def get_songs_with_url(self, raw_html):
        """
        User overrides this method to get list of songs from raw html
        :param raw_html: HTML code of web page
        :return: Songs with URL
        """
        return [('foobar.com', 'Foo Bar')]

    def get_song_details(self, raw_html):
        """
        User overrides this method to get details for a song from raw html
        :param raw_html: HTML code of web page
        :return: Structured song details
        """
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
    def __init__(self, name, start_url, list_of_url, number_of_threads,
                 delay_request=False, max_allowed_errors=3):
        """

        :param name: As usual
        :param start_url: As usual
        :param list_of_url: As usual
        :param number_of_threads: As usual
        :param delay_request: As usual
        :param max_allowed_errors: As usual
        """
        super().__init__(name, start_url, number_of_threads=number_of_threads,
                         delay_request=delay_request,
                         max_err=max_allowed_errors)
        self.url_list = list_of_url
        self.task_queue = LifoQueue()

    def run(self):
        """
        Method called from subclasses to start crawling process
        """
        while True:
            # Crawl cycle starts
            print_util.print_info(
                'Starting new crawl with {0}'.format(
                    self.name
                )
            )
            # Add all URLs to task queue
            for url in self.url_list:
                self.task_queue.put(
                    {
                        'type': 0,
                        'url': url,
                        'n_errors': 0
                    }
                )
            # Start all threads
            threads = []
            for n in range(1, self.number_of_threads + 1):
                temp_thread = Thread(
                    target=self.threader,
                    args=(n,)
                )
                threads.append(temp_thread)
                temp_thread.start()
            for temp_thread in threads:
                temp_thread.join()
                # Crawl cycle ends

    def threader(self, thread_id):
        """
        Worker function
        :param thread_id: As usual
        """
        while not self.task_queue.empty():
            task = self.task_queue.get()

            if task['n_errors'] >= self.max_allowed_errors:
                print_util.print_warning(
                    '{0} --> Too many errors in task {1}. Skipping.'.format(
                        thread_id,
                        task
                    )
                )
                continue

            print_util.print_info(
                '{0} --> New task : {1}'.format(
                    thread_id,
                    task
                )
            )

            try:
                if task['type'] == 0:
                    self.get_artists(
                        thread_id,
                        task['url']
                    )
                elif task['type'] == 1:
                    self.get_artist_albums(
                        thread_id,
                        task['url'],
                        task['artist']
                    )
                elif task['type'] == 2:
                    self.get_song(
                        thread_id,
                        task['url'],
                        task['song'],
                        task['album'],
                        task['album_url'],
                        task['artist']
                    )

                print_util.print_info(
                    '{0} --> Task complete : {1}'.format(
                        thread_id,
                        task
                    ),
                    colors.GREEN
                )
            except Exception as e:
                print_util.print_error(
                    '{0} --> Error : {1}'.format(
                        thread_id,
                        e
                    )
                )
                task['no_errors'] += 1
                self.task_queue.put(task)

    def get_artists(self, thread_id, url):
        """
        Method to get artists with URL from a web address
        :param thread_id: As usual
        :param url: As usual
        """
        website = self.start_url + url
        raw_html = open_request(website, delayed=self.delay_request)

        artists_with_url = self.get_artists_with_url(raw_html)

        for artist_url, artist in artists_with_url:
            self.task_queue.put(
                {
                    'type': 1,
                    'url': artist_url,
                    'artist': artist,
                    'n_errors': 0
                }
            )

    def get_artist_albums(self, thread_id, url, artist):
        """
        Method to get all songs for an artist
        :param thread_id: As usual
        :param url: As usual
        :param artist: Artist name
        """
        website = self.start_url + '/' + url
        raw_html = open_request(website, delayed=self.delay_request)

        albums_with_songs = self.get_albums_with_songs(raw_html)

        for album, song_with_url in albums_with_songs:
            for song_url, song in song_with_url:
                self.task_queue.put(
                    {
                        'type': 2,
                        'url': song_url,
                        'album': album,
                        'album_url': url,
                        'artist': artist,
                        'n_errors': 0
                    }
                )

    def get_song(self, thread_id, url, song, album, album_url, artist):
        """
        Method to get details of a song and save in database
        :param thread_id: As usual
        :param url: As usual
        :param song: Song title
        :param album: Album name
        :param album_url: URL of album (same as artist) on the website
        :param artist: As usual
        """
        if db_operations.exists_song(self.start_url, url):
            print_util.print_warning(
                '{0} -> Song {1} already exists. Skipping'.format(
                    thread_id,
                    song
                )
            )
            return

        song_website = self.start_url + url
        song_html = open_request(song_website, delayed=self.delay_request)
        lyrics = self.get_song_details(song_html)
        db_operations.save(
            song=song,
            song_url=url,
            movie=album,
            movie_url=album_url,
            start_url=self.start_url,
            lyrics=lyrics,
            singers=artist,
            director=artist,
            lyricist=artist
        )

    def get_artists_with_url(self, raw_html):
        """
        Get artist list from HTML code
        :param raw_html: Web page HTML code
        :return: Artists with URLs
        """
        return [('a.com', 'a'), ]

    def get_albums_with_songs(self, raw_html):
        """
        Get all songs with albums for an artist
        :param raw_html: Web page HTML code
        :return: Songs with URL and album
        """
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
        """
        Get lyrics of the song from webpage
        :param song_html:
        :return:
        """
        return 'la la la la'


class CrawlerType2(BaseCrawler):
    def __init__(self, name, start_url, list_of_urls, number_of_threads,
                 delayed_request=False, max_allowed_error=10):
        super().__init__(name, start_url, number_of_threads,
                         delay_request=delayed_request,
                         max_err=max_allowed_error)
        self.url_list = list_of_urls
        self.task_queue = LifoQueue()

    def run(self):
        """
        Function to be called by subclasses to start crawler
        """
        while True:
            # Crawl cycle starts
            print_util.print_info(
                'Starting crawl with {0}'.format(
                    self.name
                )
            )
            # Add URLs to task queue
            for url in self.url_list:
                self.task_queue.put(
                    {
                        'type': 0,
                        'url': url,
                        'n_errors': 0
                    }
                )
            # Start all threads
            threads = []
            for n in range(1, self.number_of_threads + 1):
                temp_thread = Thread(
                    target=self.threader,
                    args=(n,)
                )
                threads.append(temp_thread)
                temp_thread.start()
            # Wait for threads to finish
            for temp_thread in threads:
                temp_thread.join()
                # Crawl cycle ends

    def threader(self, thread_id):
        """
        Worker function
        :param thread_id: Ass usual
        """
        while not self.task_queue.empty():

            task = self.task_queue.get()
            if task['n_errors'] >= self.max_allowed_errors:
                print_util.print_warning(
                    '{0} --> Too many errors in task {1}. Skipping.'.format(
                        thread_id,
                        task
                    )
                )
                continue

            print_util.print_info(
                '{0} --> New task : {1}'.format(
                    thread_id,
                    task
                )
            )

            try:
                if task['type'] == 0:
                    self.get_artists(
                        thread_id,
                        task['url']
                    )
                elif task['type'] == 1:
                    self.get_artist(
                        thread_id,
                        task['url'],
                        task['artist']
                    )
                elif task['type'] == 2:
                    self.get_songs_from_page(
                        thread_id,
                        task['url'],
                        task['artist']
                    )
                elif task['type'] == 3:
                    self.get_song(
                        thread_id,
                        task['url'],
                        task['song'],
                        task['artist']
                    )
            except Exception as e:
                print_util.print_error(
                    '{0} --> Error : {1}'.format(
                        thread_id,
                        e
                    )
                )
                task['n_errors'] += 1
                self.task_queue.put(task)

    def get_artists(self, thread_id, url):

        """
        Method to get artists from a URL
        :param thread_id: As usual
        :param url: As usual
        """
        complete_url = self.start_url + url
        raw_html = open_request(complete_url, delayed=self.delay_request)

        artists_with_url = self.get_artist_with_url(raw_html)

        for artist_url, artist in artists_with_url:
            self.task_queue.put(
                {
                    'type': 1,
                    'url': artist_url,
                    'artist': artist
                }
            )

    def get_artist(self, thread_id, url, artist):
        """
        Get songs for artist from URL in two parts:
            1. Get songs from first page (:param url)
            2. Add all other pages to task queue
        :param thread_id:
        :param url:
        :param artist:
        """
        complete_url = self.start_url + url
        raw_html = open_request(complete_url, delayed=self.delay_request)

        pages = self.get_pages_for_artist(raw_html)

        # Add all songs from current page
        for song_url, song in self.get_songs(raw_html):
            self.task_queue.put(
                {
                    'type': 3,
                    'url': song_url,
                    'song': song,
                    'artist': artist
                }
            )

        # Add rest of pages in task queue
        for page in pages[1:]:
            self.task_queue.put(
                {
                    'type': 2,
                    'url': page,
                    'artist': artist
                }
            )

    def get_songs_from_page(self, thread_id, url, artist):
        """
        Get songs from other pages of artist
        :param thread_id: As usual
        :param url: As usual
        :param artist: As usual
        """
        complete_url = self.start_url + url
        raw_html = open_request(complete_url, delayed=self.delay_request)

        for song_url, song in self.get_songs(raw_html):
            self.task_queue.put(
                {
                    'type': 3,
                    'url': song_url,
                    'song': song,
                    'artist': artist
                }
            )

    def get_song(self, thread_id, url, song, artist):
        """
        Get song from a URL
        :param thread_id: As usual
        :param url: As usual
        :param song: As usual
        :param artist: Artist of song
        """
        complete_url = self.start_url + url
        raw_html = open_request(complete_url, delayed=self.delay_request)

        album, lyrics, lyricist, additional_artists = self.get_song_details(
            raw_html
        )  # Note: additional_artists are artist(s) featured in the song

        db_operations.save(
            song,
            url,
            album,
            url,
            self.start_url,
            lyrics,
            additional_artists + [artist, ],
            [artist, ],
            lyricist
        )

    def get_song_details(self, raw_html):
        """
        User overrides this method to get details about a song
        :param raw_html: HTML code of web page
        :return: Song details
        """
        return (
            'album',
            'lyrics',
            [
                'lyricist1',
                'lyricist2'
            ],
            [
                'additional_artist1',
                'additional_artist2',
            ]
        )

    def get_artist_with_url(self, raw_html):
        """
        User overrides this method to get all artists with URL from a web page
        :param raw_html: HTML code of web page
        :return: Artists with URLs
        """
        return [
            ('url1', 'artist1'),
            ('url2', 'artist2')
        ]

    def get_pages_for_artist(self, raw_html):
        """
        Get a list of pages for an artist from given HTML code
        :param raw_html: HTML code of web page
        :return: List of URLs
        """
        return [
            'url1',
            'url2'
        ]

    def get_songs(self, raw_html):
        """
        User overrides this function to get songs with URL from page's HTML
        :param raw_html: HTML code for web page
        :return: Songs with URLs
        """
        return [
            ('url1', 'song1'),
            ('url2', 'song2')
        ]