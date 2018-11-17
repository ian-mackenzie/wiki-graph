import logging
from threading import Thread
from queue import Queue
from scraper import scrape_page
from time import time
import pymongo
import asyncio
from motor import motor_asyncio
import pprint

client = motor_asyncio.AsyncIOMotorClient('localhost', 27017)
db = client["wiki-graph-py"]
db.pages.drop()
db.edges.drop()
pages = db["pages"]
edges = db["edges"]
pages.create_index([("title", pymongo.TEXT)], unique=True)


# Graph = namedtuple('Graph', ('nodes', 'edges'))

# graph = Graph(set([]), set([]))

async def linkHandler(parent_url, link_url, queue, depth):
    
    count = await db.pages.find_one({'title': link_url})
    if not count:
        try:
            await pages.insert_one({"title": link_url})
        except pymongo.errors.DuplicateKeyError as error:
            pprint.pprint(error)

        if depth > 0:
            queue.put((link_url, depth-1))
    # graph.edges.add((url, link_url))
    await edges.insert_one({"parent": parent_url,"child": link_url})

class ScrapeWorker(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue
        self.event_loop = asyncio.new_event_loop()

    def run(self):
        while True:
            url, depth =  self.queue.get()
            try:
                links = scrape_page(url)
                for link_url in links:
                    self.event_loop.run_until_complete(linkHandler(url, link_url, self.queue, depth))
            finally:
                print(url + ' depth ' + str(depth) + ' done!')
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

    # with open('output/graph.json', 'w') as outfile:
    #     json.dump({
    #         'nodes':list(graph.nodes),
    #         'edges':list(graph.edges)
    #     }, outfile)

    logging.info('Took %s', time() - ts)


if __name__ == '__main__':
    main('History', 2)