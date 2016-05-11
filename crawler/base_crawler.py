from queue import Queue

class BaseCrawler:
    def __init__(self, name, start_url):
        self.name = name
        self.start_url = start_url


class CrawlerType0(BaseCrawler):

    task_queue = Queue()

    def __init__(self, name, start_url, list_of_url, number_of_threads):
        super().__init__(name, start_url)
        self.url_list = list_of_url
        self.number_of_threads = number_of_threads

    @staticmethod
    def run():
        pass