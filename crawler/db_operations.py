from psycopg2 import connect


def get_connection():
    conn = connect(database='lyrics', user='lyrics', password='lyrics',
                   host='localhost', port='5432')

    return conn, conn.cursor()


def create():
    sql = '''CREATE TABLE IF NOT EXISTS songs (
              id BIGSERIAL PRIMARY KEY NOT NULL ,
              song TEXT,
              song_url VARCHAR(512),
              movie TEXT,
              movie_url VARCHAR(512),
              start_url VARCHAR(512),
              lyrics TEXT,
              singers TEXT,
              director TEXT,
              lyricist TEXT,
              last_crawled TIMESTAMP,
              last_updated TIMESTAMP
            );'''

    conn, cur = get_connection()
    cur.execute(sql)
    conn.commit()
    conn.close()


def save(song, song_url, movie, movie_url, start_url, lyrics, singers,
         director, lyricist):
    sql = """SELECT id FROM songs WHERE song_url=%s AND start_url=%s;"""

    conn, cur = get_connection()

    cur.execute(
        sql,
        (
            song_url,
            start_url
        )
    )

    result = cur.fetchall()
    if len(result) == 0:
        sql = """INSERT INTO songs(
                    song, song_url, movie, movie_url, start_url, lyrics,
                    singers, director, lyricist, last_updated, last_crawled
                  )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP,
                 CURRENT_TIMESTAMP) RETURNING id;"""

        cur.execute(
            sql,
            (
                song,
                song_url,
                movie,
                movie_url,
                start_url,
                lyrics,
                str(singers),
                str(director),
                str(lyricist)
            )
        )
    else:
        sql = """UPDATE table songs SET song=%s, song_url=%s, movie=%s,
        movie_url=%s, start_url=%s, lyrics=%s, singers=%s, director=%s,
        lyricist=%s, last_updated=CURRENT_TIMESTAMP,
        last_crawled=CURRENT_TIMESTAMP WHERE id=%s RETURNING id;"""

        cur.execute(
            sql,
            (
                song,
                song_url,
                movie,
                movie_url,
                start_url,
                lyrics,
                str(singers),
                director,
                lyricist,
                result[0][0]
            )
        )

    result = cur.fetchall()[0][0]
    conn.commit()
    conn.close()
    return result


def load(id):
    sql = """SELECT * FROM songs WHERE id=%s;"""

    conn, cur = get_connection()

    cur.execute(
        sql,
        (
            id,
        )
    )
    result = cur.fetchall()

    conn.close()

    return result[0][1:]


def is_old_movie(start_url, url):
    sql = """SELECT count(*) FROM songs WHERE start_url=%s AND movie_url=%s;"""

    conn, cur = get_connection()

    cur.execute(
        sql,
        (
            start_url,
            url
        )
    )

    if cur.fetchall()[0][0] == 0:  # No such movie exists
        return False

    sql = """SELECT date_part('month', age((SELECT last_updated FROM songs WHERE
 start_url=%s AND movie_url=%s LIMIT 1)));"""

    cur.execute(
        sql,
        (
            start_url,
            url
        )
    )

    result = cur.fetchall()
    conn.close()
    return result[0][0] >= 6


def update_last_crawl(start_url, url):
    sql = """UPDATE table songs SET last_crawled=CURRENT_TIMESTAMP WHERE
start_url=%s AND movie_url=%s;"""

    conn, cur = get_connection()

    conn.execute(
        sql,
        (
            start_url,
            url
        )
    )

    conn.commit()
    conn.close()


def number_of_songs(start_url, url):
    sql = """SELECT count(*) FROM songs WHERE start_url=%s AND movie_url=%s;"""

    conn, cur = get_connection()

    cur.execute(
        sql,
        (
            start_url,
            url
        )
    )

    result = cur.fetchall()[0][0]
    conn.close()
    return result
