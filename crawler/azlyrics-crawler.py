from random import shuffle
from re import findall, DOTALL
from string import ascii_lowercase

from base_crawler import CrawlerType1


class AZLyricsCrawler(CrawlerType1):
    def __init__(self, name, start_url, url_list, number_of_threads,
                 delayed_request=True, max_errors=3):
        super().__init__(name, start_url, url_list, number_of_threads,
                         delay_request=delayed_request,
                         max_allowed_errors=max_errors)

    def get_artists_with_url(self, raw_html):
        refined = findall(
            r'<div class=\"col-sm-6 text-center artist-col\">(.*?)</div>  '
            r'<!-- container main-page -->',
            raw_html,
            DOTALL
        )[0]

        result = findall(
            r'<a href=\"(.*?)\">(.*?)<',
            refined,
            DOTALL
        )

        shuffle(result)

        return result

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
            )

            if len(album_name) == 0:
                album_name = 'other'
            else:
                album_name = album_name[0]

            songs_with_url = findall(
                r'<a href=\"\.\.(.*?)\" target=\"_blank\">(.*?)</a><br>',
                content
            )
            data.append(
                (
                    album_name,
                    songs_with_url
                )
            )

        shuffle(data)
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
        1,
        max_errors=5,
        delayed_request=True
    )

    crawler.run()


if __name__ == "__main__":
    main()
