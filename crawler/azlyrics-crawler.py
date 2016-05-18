import sys
from random import shuffle
from re import findall, DOTALL
from string import ascii_lowercase

from base_crawler import CrawlerType1


class AZLyricsCrawler(CrawlerType1):
    def __init__(self, name, start_url, url_list, number_of_threads):
        super().__init__(name, start_url, url_list, number_of_threads)

    def get_artists_with_url(self, raw_html):
        refined = findall(
            r'<div class=\"col-sm-6 text-center artist-col\">(.*?)</div>  '
            r'<!-- container main-page -->',
            raw_html,
            DOTALL
        )[0]

        return findall(
            r'<a href=\"(.*?)\">(.*?)<',
            refined,
            DOTALL
        )

    def get_albums_with_songs(self, raw_html):
        data = []

        album_html = findall(
            r'iv class=\"album\">(.*?)<d',
            raw_html,
            DOTALL
        )

        for content in album_html:
            album_name = findall(
                r'<b>\"(.*?)\"',
                content,
                DOTALL
            )[0]

            songs_with_url = findall(
                r'<a href=\"(\.\..*?)\" target=\"_blank\">(.*?)</a><br>',
                content
            )
            data.append(
                (
                    album_name,
                    songs_with_url
                )
            )

        return data

    def get_song_details(self, song_html):
        return findall(
            r'<div>.*?-->(.*?)</div>',
            song_html,
            DOTALL
        )[0].replace(
            '<br>',
            '\n'
        ).replace(
            '<i>',
            ''
        ).replace(
            '</i>',
            ''
        )


def main():
    list_of_initials = ['19', ] + list(ascii_lowercase)

    shuffle(list_of_initials)

    crawler = AZLyricsCrawler(
        'AZ Lyrics Crawler',
        'http://azlyrics.com',
        ['/{0}.html'.format(i) for i in list_of_initials],
        int(sys.argv[1])
    )

    crawler.run()


if __name__ == "__main__":
    main()
