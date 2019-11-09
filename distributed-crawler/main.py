import asyncio
import logging
from asyncio import Queue

import yaml
from aio_pika import connect_robust
from aio_pika.patterns import Master
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

current_crawls = set()


async def pusher(article_queue: Queue, es: Elasticsearch) -> None:
    while True:
        article = await article_queue.get()
        logging.info(article.url)
        try:
            await es.index('sites', '_doc', id=article.url, body={
                'title': article.title,
                'site': article.site,
                'url': article.url,
            })
        except Exception as e:
            logging.error(e)
        article_queue.task_done()


async def index(url, *args, **kwargs):
    logging.info(f'add index job: {url}')
    crawler = Crawler(*args, **kwargs)
    await crawler.add_crawl(url)
    await crawler.join()


async def main():
    with open('config.yml', 'r') as config_file:
        config = yaml.load(config_file)

    amqp_endpoint = config.get('amqp_endpoint', 'amqp://guest:guest@broker/')
    es_endpoint = config.get('es_endpoint', 'http://elasticsearch:9200')
    crawler_concurrency = config.get('crawler_concurrency', 10)
    pusher_concurrency = config.get('pusher_concurrency', 10)
    rate = config.get('rate', 10)

    async with Elasticsearch(es_endpoint, retry_on_timeout=True, max_retries=10) as es:
        if not await es.indices.exists(INDEX_NAME):
            try:
                await es.indices.create(INDEX_NAME, mapping)
            except Exception as e:
                logging.warning(e)

        article_queue = asyncio.Queue()
        for _ in range(pusher_concurrency):
            asyncio.create_task(pusher(article_queue, es))

        async def worker(*, domain: str, https: bool):
            url = f'{"https" if https else "http"}://{domain}/'
            asyncio.create_task(index(url,
                                      article_queue=article_queue,
                                      concurrency=crawler_concurrency,
                                      rate=rate))

        connection = await connect_robust(amqp_endpoint)
        channel = await connection.channel()
        master = Master(channel)
        await master.create_worker('index', worker, auto_delete=True)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
