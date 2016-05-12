from psycopg2 import connect


def get_connection():
    conn = connect(database='lyrics', user='lyrics', password='lyrics',
                   host='localhost', port='5432')

    return conn, conn.cursor()


def create():
    sql = '''CREATE TABLE IF NOT EXISTS songs (
              id BIGSERIAL PRIMARY KEY NOT NULL ,
              song text,
              song_url text,
              movie text,
              movie_url TEXT,
              start_url text,
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
