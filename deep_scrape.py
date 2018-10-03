import logging
from threading import Thread
from queue import Queue
from scraper import scrape_page
from time import time
from collections import namedtuple
import json

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
                    if (depth > 0) and not link_url in graph.nodes:
                        self.queue.put((link_url, depth-1))
                    graph.nodes.add(link_url)
                    graph.edges.add((url, link_url))
            finally:
                print(url + ' depth ' + depth + ' done!')
                self.queue.task_done()


def main(url, depth):
    ts = time()
    queue = Queue()

    for x in range(20):
        worker = ScrapeWorker(queue)
        worker.daemon = True
        worker.start()

    queue.put((url, depth))

    queue.join()
    with open('output/graph.json', 'w') as outfile:
        json.dump({
            'nodes':list(graph.nodes),
            'edges':list(graph.edges)
        }, outfile)
    logging.info('Took %s', time() - ts)


if __name__ == '__main__':
    main('/wiki/History', 2)