import sys
from re import findall, DOTALL
from string import ascii_lowercase

from base_crawler import CrawlerType0


class LyricsMastiCrawler(CrawlerType0):
    def __init__(self, name, start_url, list_of_url, number_of_threads):
        super().__init__(name, start_url, list_of_url, number_of_threads)

    def get_movies_with_url(self, raw_html):
        refined = findall(
            r'<ul class="list-group list-group-flush">(.*?)</ul>',
            raw_html,
            DOTALL
        )[0]

        url_movie = findall(
            r'<a href=\"(.*?)\">\n(.*?)</a>',
            refined,
            DOTALL
        )

        return [(url, movie.strip(' \t\n\r')) for url, movie in url_movie]

    def get_songs_with_url(self, raw_html):
        refined = findall(
            r'<ol class="custom-counter">(.*?)</ol>',
            raw_html,
            DOTALL
        )[0]

        song_url = findall(
            r'<a.*?href=\"(.*?)\".*?3>(.*?)<',
            refined,
            DOTALL
        )

        return [(url, song.strip(' \t\n\r')) for url, song in song_url]

    def get_song_details(self, raw_html):
        refined = findall(
            r'<ul>(.*?)</ul>',
            raw_html,
            DOTALL
        )[0]

        singers = modify_artist(
            findall(
                r'<h4>S.*?set.*?>(.*?)<',
                refined,
                DOTALL
            )
        )

        lyricists = modify_artist(
            findall(
                r'<h4>L.*?set.*?>(.*?)<',
                refined,
                DOTALL
            )
        )

        directors = modify_artist(
            findall(
                r'<h4>M.*?set.*?>(.*?)<',
                refined,
                DOTALL
            )
        )

        lyrics = findall(
            r'v><code.*?>(.*?)</',
            raw_html,
            DOTALL
        )[0]

        return lyrics, singers, directors, lyricists


def modify_artist(artist):
    if len(artist) > 0:
        return artist[0].strip(' \t\n\r').replace(
            ' &amp;',
            ', '
        ).split(', ')
    else:
        return []


def main():
    dict_pages = {
        '%23': 2,
        'a': 17,
        'b': 11,
        'c': 7,
        'd': 14,
        'e': 3,
        'f': 3,
        'g': 6,
        'h': 8,
        'i': 3,
        'j': 8,
        'k': 11,
        'l': 4,
        'm': 12,
        'n': 5,
        'o': 2,
        'p': 9,
        'q': 1,
        'r': 6,
        's': 13,
        't': 6,
        'u': 2,
        'v': 2,
        'w': 2,
        'x': 1,
        'y': 3,
        'z': 2
    }

    list_of_initials = ['%23', ] + list(ascii_lowercase[:])

    list_of_websites = []
    for initial in list_of_initials:
        for page in range(1, dict_pages[initial] + 1):
            list_of_websites.append(
                '/songs_for_movie_{0}.html?page={1}'.format(
                    initial,
                    page
                )
            )

    crawler = LyricsMastiCrawler(
        'LyricsMasti Crawler',
        'http://www.lyricsmasti.com',
        list_of_websites,
        int(sys.argv[1])
    )

    crawler.run()


if __name__ == "__main__":
    main()
