import asyncio
from argparse import ArgumentParser
from asyncio import Queue
from aioelasticsearch import Elasticsearch
from crawler import Crawler

mapping = {
    'mappings': {
        'properties': {
            'title': {'type': 'text'},
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
    parser = ArgumentParser(description='Process some integers.')
    parser.add_argument('urls', metavar='URL', nargs='+',
                        help='urls to crawl')
    parser.add_argument('-e', '--es-host',
                        help='elasticsearch url')
    parser.add_argument('-c', '--crawler-concurrency', type=int, default=10,
                        help='crawler concurrency')
    parser.add_argument('-p', '--pusher-concurrency', type=int, default=10,
                        help='db pusher concurrency')
    parser.add_argument('-r', '--rate', type=int, default=10,
                        help='crawler request rate')
    args = parser.parse_args()

    async with Elasticsearch(args.es_host, retry_on_timeout=True, max_retries=10) as es:
        if not await es.indices.exists(INDEX_NAME):
            try:
                await es.indices.create(INDEX_NAME, mapping)
            except Exception as e:
                print(e)

        article_queue = asyncio.Queue()
        crawler = Crawler(article_queue=article_queue,
                          concurrency=args.crawler_concurrency,
                          rate=args.rate)
        for url in args.urls:
            await crawler.add_crawl(url)

        consumers = [asyncio.create_task(pusher(article_queue, es))
                     for _ in range(args.pusher_concurrency)]

        await crawler.join()
        await article_queue.join()
        for c in consumers:
            c.cancel()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
