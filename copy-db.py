import sys

from psycopg2 import connect


def get_host_connection():
    conn = connect(
        database='lyrics',
        user='lyrics',
        password='lyrics',
        host=sys.argv[1],
        port='5432'
    )
    return conn, conn.cursor()


def get_own_connection():
    conn = connect(
        database='lyrics',
        user='lyrics',
        password='lyrics',
        host='127.0.0.1',
        port='5432'
    )

    return conn, conn.cursor()


def copy():
    sql = 'select * from songs;'

    conn, cur = get_host_connection()

    cur.execute(sql)

    all_data = cur.fetchall()

    conn.close()

    conn, cur = get_own_connection()

    for data in all_data:
        print('Inserting data with key {0}'.format(data[0]))
        sql = 'INSERT INTO songs(song, song_url, movie, movie_url, start_url,' \
              ' lyrics, singers, director, lyricist, last_updated,' \
              ' last_crawled) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,' \
              ' %s);'
        cur.execute(
            sql,
            tuple(data[1:])
        )

    conn.commit()
    conn.close()
