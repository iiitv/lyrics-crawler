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
                (
                    url.replace('http://www.metrolyrics.com', ''),
                    artist.replace(' Lyrics', '').strip(' \n')
                )
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

        links = findall(
            r'<a href="(.*?)"',
            area_of_interest,
            DOTALL
        )

        return [link.replace('http://www.metrolyrics.com', '') for link in
                links]

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
                (
                    url.replace('http://www.metrolyrics.com', ''),
                    song.replace(' Lyrics', '').strip(' \n'))
            )

        return songs_with_url


def main():
    pages_dict = {
        '1': 8,  # 8
        'a': 85,  # 85
        'b': 81,  # 81
        'c': 81,  # 81
        'd': 81,  # 81
        'e': 42,  # 42
        'f': 39,  # 39
        'g': 42,  # 42
        'h': 37,  # 37
        'i': 21,  # 21
        'j': 77,  # 77
        'k': 47,  # 47
        'l': 62,  # 62
        'm': 94,  # 94
        'n': 36,  # 36
        'o': 17,  # 17
        'p': 50,  # 50
        'q': 3,  # 3
        'r': 57,  # 57
        's': 100,  # 100
        't': 100,  # 100
        'u': 8,  # 8
        'v': 18,  # 18
        'w': 26,  # 26
        'x': 3,  # 3
        'y': 19,  # 13
        'z': 8  # 8
    }

    l = ['1', ] + list(ascii_lowercase)

    list_of_url = []

    for x in l:
        for y in range(1, pages_dict[x] + 1):
            list_of_url.append(
                '/artists-{0}-{1}.html'.format(
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
