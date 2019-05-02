import asyncio
from asyncio import Queue
from aioelasticsearch import Elasticsearch
from crawler import Crawler

mapping = {
    'mappings': {
        'properties': {
            'title': {'type': 'keyword'},
            'url': {'type': 'keyword'},
            'site': {'type': 'keyword'},
        },
    },
}

INDEX_NAME = 'sites'


async def pusher(article_queue: Queue, es: Elasticsearch):
    while True:
        article = await article_queue.get()
        print(article.url)
        try:
            await es.index('sites', '_doc', id=article.url, body={
                'title': article.title,
                'site': article.site,
                'url': article.url,
            })
        except Exception as e:
            print(e)
        article_queue.task_done()


async def main():
    url = 'https://docs.python.org/3/'
    es_endpoint = 'http://localhost:9200'

    async with Elasticsearch(es_endpoint, retry_on_timeout=True, max_retries=10) as es:
        if not await es.indices.exists(INDEX_NAME):
            try:
                await es.indices.create(INDEX_NAME, mapping)
            except Exception as e:
                print(e)

        article_queue = asyncio.Queue()
        crawler = Crawler(article_queue=article_queue)
        await crawler.add_crawl(url)

        consumers = [asyncio.create_task(pusher(article_queue, es)) for _ in range(1)]

        await crawler.join()
        await article_queue.join()
        for c in consumers:
            c.cancel()


if __name__ == '__main__':
    asyncio.run(main())
