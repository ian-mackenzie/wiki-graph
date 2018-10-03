import logging
from threading import Thread
from queue import Queue
from scraper import scrape_page
from time import time
from collections import namedtuple

Graph = namedtuple('Graph', ('nodes', 'edges'))

graph = Graph(set([]), set([]))

class ScrapeWorker(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            url, depth =  self.queue.get()
            try:
                links = scrape_page(url)
                for link_url in links:
                    graph.nodes.add(link_url)
                    graph.edges.add((url, link_url))
                    if (depth > 0):
                        self.queue.put((link_url, depth-1))
            finally:
                print(url + ' done!')
                self.queue.task_done()


def main(url, depth):
    ts = time()
    queue = Queue()

    for x in range(8):
        worker = ScrapeWorker(queue)
        worker.daemon = True
        worker.start()

    queue.put((url, depth))

    queue.join()
    print(graph)
    logging.info('Took %s', time() - ts)


if __name__ == '__main__':
    main('/wiki/History', 3)