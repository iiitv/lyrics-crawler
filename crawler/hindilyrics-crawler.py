import sys
from re import findall, DOTALL
from string import ascii_lowercase

from base_crawler import CrawlerType0


class HindilyricsCrawler(CrawlerType0):
    def __init__(self, name, start_url, list_of_url, number_of_threads):
        super().__init__(name, start_url, list_of_url, number_of_threads)

    def get_movies_with_url(self, raw_html):
        return findall(r'<li>.*?\"(.*?)\">(.*?)<', raw_html)

    def get_songs_with_url(self, raw_html):
        return findall(r'<li>.*?\"(.*?)\">(.*?)<', raw_html)

    def get_song_details(self, raw_html):
        singers = modify_artist(findall(r'Singer\(s\).*?:(.*?)<br>', raw_html))
        music_by = modify_artist(findall(r'Music By.*?:(.*?)<br>', raw_html))
        lyricists = modify_artist(findall(r'Lyricist.*?:(.*?)<br>', raw_html))

        lyrics = findall(
            r'<font face="verdana\">(.*?)</font',
            raw_html,
            DOTALL
        )[0]

        lyrics.replace(
            '\\\\n',
            '\n'
        ).replace(
            '\\r',
            ''
        )

        return lyrics, singers, music_by, lyricists


def modify_artist(artist):
    if len(artist) > 0:
        return findall(
            r'\">(.*?)<',
            artist[0]
        )
    else:
        return []


def main():
    dict_pages = {
        '0': 1,
        'a': 6,
        'b': 4,
        'c': 3,
        'd': 4,
        'e': 1,
        'f': 1,
        'g': 2,
        'h': 3,
        'i': 2,
        'j': 3,
        'k': 4,
        'l': 2,
        'm': 4,
        'n': 2,
        'o': 1,
        'p': 3,
        'q': 1,
        'r': 2,
        's': 4,
        't': 2,
        'u': 1,
        'v': 1,
        'w': 1,
        'y': 1,
        'z': 1
    }

    list_of_initials = ['0', ] + list(ascii_lowercase[:])
    list_of_initials.remove('x')

    list_of_websites = []
    for initial in list_of_initials:
        for page in range(1, dict_pages[initial]):
            list_of_websites.append(
                '/lyrics/hindi-songs-starting-{0}-page-{1}.html'.format(
                    initial,
                    page
                )
            )

    crawler = HindilyricsCrawler(
        'hindilyrics-crawler',
        'http://www.hindilyrics.net',
        list_of_websites,
        int(sys.argv[1])
    )

    crawler.run()


if __name__ == "__main__":
    main()
