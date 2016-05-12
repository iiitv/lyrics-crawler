from psycopg2 import connect


def get_connection():
    conn = connect(database='lyrics', user='lyrics', password='lyrics',
                   host='localhost', port='5432')

    return conn, conn.cursor()


def create():
    sql = '''CREATE TABLE IF NOT EXISTS songs (
              id BIGSERIAL PRIMARY KEY NOT NULL ,
              song VARCHAR(50),
              song_url VARCHAR(1024),
              movie VARCHAR(50),
              movie_url VARCHAR(50),
              start_url VARCHAR(1024),
              lyrics TEXT,
              singers VARCHAR(500),
              director VARCHAR(50),
              lyricist VARCHAR(50)
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
