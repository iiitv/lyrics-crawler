from queue import Queue
from re import findall, DOTALL
from string import ascii_lowercase
from threading import Thread
from urllib import request

from print_util import print_error, print_info

task_queue = Queue()
location = 'downloads/'
start_address = 'http://smriti.com'


def download_movie(thread_id, init, url, movie):
    return


def get_movies(thread_id, init):
    global start_address

    print_info('{0} : Getting webpage for movies starting with \'{'
               '1}\''.format(thread_id, init))
    website = start_address + '/hindi-songs/movies-{0}'.format(init)
    done = False
    raw_html = ''
    hdr = {'User-Agent': 'Mozilla/5.0'}
    while not done:
        try:
            req = request.Request(website, headers=hdr)
            raw_html = str(request.urlopen(req).read())
            done = True
        except Exception as e:
            print_error('{0} : Error occurred while getting {1}, '
                        'retrying'.format(thread_id, website))

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


def main(number_of_threads):
    thread_dict = {}
    for i in range(1, number_of_threads + 1):
        temp = Thread(target=movie_threader, args=(i,))
        temp.start()
        thread_dict[i] = temp

    crawl_list = ['1', ] + list(ascii_lowercase)
    crawl_list.remove('x')
    for i in crawl_list:
        task_queue.put((0, i))

    for i in range(1, number_of_threads + 1):
        thread_dict[i].join()


if __name__ == "__main__":
    main(4)
