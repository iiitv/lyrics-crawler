from queue import Queue
from re import findall, DOTALL
from urllib import request

from print_util import print_error, print_info

task_queue = Queue()
location = 'downloads/'
start_address = 'http://www.smriti.com'


def download_movie(thread_id, init, url, movie):
    pass


def get_movies(thread_id, init):
    global start_address

    print_info('{0} : Getting webpage for movies starting with \'{'
               '1}\''.format(thread_id, init))
    website = start_address + '/hindi-sings/movie-{0}'.format(init)
    done = False
    raw_html = ''
    while not done:
        try:
            raw_html = str(request.urlopen(website).open())
            done = True
        except Exception:
            print_error('{0} : Error occurred, retrying')

    main_content = findall(r'<a href=\"/hindi-songs/\">main index</a>('
                           r'.*?)</div>', raw_html, DOTALL)[0]
    movies_with_url = findall(r'<a href=\"(.*?)\">(.*?)</a>', main_content)
    for url, movie in movies_with_url:
        init = '0' if init == '1' else init
        movie = movie.replace('/', '_').replace(':', '_').replace('-', '_')
        task_queue.put((1, init, url, movie))


def movie_threader(thread_id):
    while True:
        task = task_queue.get()

        if task[0] == 0:
            get_movies(thread_id, task[1])
        elif task[0] == 1:
            download_movie(thread_id, task[1], task[2], task[3])


def main():
    return


if __name__ == "__main__":
    main()
