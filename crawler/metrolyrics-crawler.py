import sys
from re import findall, DOTALL, sub
from string import ascii_lowercase

from base_crawler import CrawlerType2


class MetroLyricsCrawler(CrawlerType2):
    def __init__(self, name, start_url, url_list, number_of_threads):
        super().__init__(name, start_url, url_list, number_of_threads)

    def get_song_details(self, raw_html):
        lyrics = findall(
            r'<div id="lyrics-body-text" class="js-lyric-text">\n(.*?)</div>\n</div>\n<p',
            raw_html,
            DOTALL
        )

        if len(lyrics) == 0:
            lyrics = findall(
                r'<div id="lyrics-body-text" class="js-lyric-text">(.*?)</div>',
                raw_html,
                DOTALL
            )[0]
        else:
            lyrics = lyrics[0]

        lyrics = sub(
            r'<div class="author">.*?</div>.*?<p class=.*?',
            '',
            lyrics
        ).replace(
            '<p class=\'verse\'>',
            ''
        ).replace(
            '<br>',
            '\n'
        ).replace(
            '</p>',
            '\n\n'
        )

        album = findall(
            r'<em>from.*?>(.*?)<',
            raw_html,
            DOTALL
        )

        album = album[0] if len(album) > 0 else ''

        lyricists = findall(
            r'<p class="writers"><strong>Songwriters</strong><br/>(.*?)</',
            raw_html,
            DOTALL
        )

        lyricists = lyricists[0].strip(' \n').split(', ') if len(
            lyricists) > 0 else []

        other_artists = findall(
            r'<p class="fea.*?span.*?>(.*?)</',
            raw_html,
            DOTALL
        )

        other_artists = other_artists[0].split(', ') if len(
            other_artists) > 0 else []

        return album, lyrics, lyricists, other_artists

    def get_artist_with_url(self, raw_html):
        data = findall(
            r'<tr itemscope itemtype="http://schema.org/MusicGroup">.*?<a '
            r'href="(.*?)".*?">(.*?)</a>.*?</tr>',
            raw_html,
            DOTALL
        )

        result = []

        for url, artist in data:
            result.append(
                (url, artist.replace(' Lyrics', '').strip(' \n'))
            )

        return result

    def get_pages_for_artist(self, raw_html):
        area_of_interest = findall(
            r'<span class="pages">(.*?)</span>',
            raw_html,
            DOTALL
        )

        if len(area_of_interest) == 0:
            return []
        else:
            area_of_interest = area_of_interest[0]

        return findall(
            r'<a href="(.*?)"',
            area_of_interest,
            DOTALL
        )

    def get_songs(self, raw_html):
        area_of_interest = findall(
            r'<tbody>(.*?)</tbody>',
            raw_html,
            DOTALL
        )

        if len(area_of_interest) == 0:
            return []

        area_of_interest = area_of_interest[0]

        _songs_with_url = findall(
            r'<tr>.*?<td>.*?<a href="(.*?)" .*?>(.*?)</a>',
            area_of_interest,
            DOTALL
        )

        songs_with_url = []

        for url, song in _songs_with_url:
            songs_with_url.append(
                (url, song.replace(' Lyrics', '').strip(' \n'))
            )

        return songs_with_url


def main():
    pages_dict = {
        '1': 0,  # 8
        'a': 0,  # 85
        'b': 0,  # 81
        'c': 0,  # 81
        'd': 0,  # 81
        'e': 0,  # 42
        'f': 0,  # 39
        'g': 0,  # 42
        'h': 0,  # 37
        'i': 0,  # 21
        'j': 0,  # 77
        'k': 0,  # 47
        'l': 0,  # 62
        'm': 0,  # 94
        'n': 0,  # 36
        'o': 0,  # 17
        'p': 0,  # 50
        'q': 0,  # 3
        'r': 0,  # 57
        's': 100,  # 100
        't': 0,  # 100
        'u': 0,  # 8
        'v': 0,  # 18
        'w': 0,  # 26
        'x': 0,  # 3
        'y': 0,  # 13
        'z': 0  # 8
    }

    l = ['1', ] + list(ascii_lowercase)

    list_of_url = []

    for x in l:
        for y in range(1, pages_dict[x] + 1):
            list_of_url.append(
                'http://www.metrolyrics.com/artists-{0}-{1}.html'.format(
                    x,
                    y
                )
            )

    crawler = MetroLyricsCrawler(
        'Metro Lyrics Crawler',
        'http://www.metrolyrics.com',
        list_of_url,
        int(sys.argv[1])
    )

    crawler.run()


if __name__ == "__main__":
    main()
