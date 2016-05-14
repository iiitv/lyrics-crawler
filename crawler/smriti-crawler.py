import sys
from re import findall, DOTALL
from string import ascii_lowercase

from base_crawler import CrawlerType0


class SmritiCrawler(CrawlerType0):
    def __init__(self, name, start_url, list_of_url, number_of_threads):
        super().__init__(name, start_url, list_of_url, number_of_threads)

    def get_movies_with_url(self, raw_html):
        main_content = findall(
            r'<a href=\"/hindi-songs/\">main index</a>(.*?)</div>',
            raw_html,
            DOTALL
        )[0]

        return findall(r'<a href=\"(.*?)\">(.*?)</a>', main_content)

    def get_songs_with_url(self, raw_html):
        return [
            (b, a.replace('.', '')) for a, b in findall(
                r'<div class="onesong">(.*?): <a href=.*?<a href="(.*?)">',
                raw_html,
                DOTALL
            )
            ]

    def get_song_details(self, raw_html):
        singers = modify_artist(
            findall(
                r'<li><b>Singer\(s\):</b> <.*?>(.*?)</',
                raw_html,
                DOTALL
            )
        )

        directors = modify_artist(
            findall(
                r'<li><b>Mu.*?:</b> <.*?>(.*?)</',
                raw_html,
                DOTALL
            )
        )

        lyricists = modify_artist(
            findall(
                r'<li><b>L.*?:</b> <.*?>(.*?)</',
                raw_html,
                DOTALL
            )
        )

        lyrics = findall(
            r'<div class=\"son.*?>(.*?)</div>',
            raw_html,
            DOTALL
        )[0].replace(
            '<br>',
            '\n'
        ).replace(
            '<p>',
            ''
        ).replace(
            '</p>',
            '\n\n'
        ).replace(
            '<br/>',
            '\n'
        )

        return lyrics, singers, directors, lyricists


def modify_artist(artist):
    if len(artist) > 0:
        return artist[0].split(', ')
    else:
        return []


def main():
    initials = [1, ] + list(ascii_lowercase)
    initials.remove('x')

    urls = []
    for element in initials:
        urls.append(
            '/hindi-songs/movies-{0}'.format(element)
        )

    crawler = SmritiCrawler('Smriti', 'http://smriti.com', urls,
                            int(sys.argv[1]))

    crawler.run()


if __name__ == "__main__":
    main()
