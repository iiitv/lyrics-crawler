from psycopg2 import connect


def get_connection():
    conn = connect(database='lyrics', user='lyrics', password='lyrics',
                   host='localhost', port='5432')

    return conn, conn.cursor()


def create():
    sql = '''CREATE TABLE IF NOT EXISTS songs (
              id BIGSERIAL PRIMARY KEY NOT NULL ,
              song text,
              song_url VARCHAR(512),
              movie text,
              movie_url VARCHAR(512),
              start_url VARCHAR(512),
              lyrics TEXT,
              singers TEXT,
              director TEXT,
              lyricist TEXT
            );'''

    conn, cur = get_connection()
    cur.execute(sql)
    conn.commit()
    conn.close()


def save(song, song_url, movie, movie_url, start_url, lyrics, singers,
         director, lyricist):
    pass


def load(id):
    pass


def is_old_movie(start_url, url):
    return False


def update_last_crawl(start_url, url):
    pass


def number_of_songs(start_url, url):
    return 0
