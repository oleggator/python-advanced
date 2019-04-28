import asyncio
import collections
import re
from asyncio import Queue
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse

import html2text
from aiohttp import ClientSession
from asyncio_throttle import Throttler


@dataclass
class Article:
    title: str
    site: str
    url: str
    content: str

    def __hash__(self):
        return hash(self.url)


class LinkQueue(Queue):
    def _init(self, maxsize):
        self._queue = collections.deque()
        self._put_items = set()

    def _get(self):
        return self._queue.popleft()

    def _put(self, item):
        root_url, url = item
        full_url = urljoin(root_url, url)

        if full_url not in self._put_items:
            self._put_items.add(full_url)
            self._queue.append(item)


class Crawler:
    html_regex = b'<title>(.*?)</title>.*?<body>(.*?)</body>'
    link_regex = b'<a.+?href=\"(.+?)\".*?>.*?</a>'

    def __init__(self, rate: int = 10, concurrency: int = 5, article_queue: Queue = None):
        self.h = html2text.HTML2Text()
        self.h.ignore_links = True

        self.throttler = Throttler(rate)

        self.concurrency = concurrency

        self.article_queue = article_queue or Queue()
        self.link_queue = LinkQueue()

        self.producers = [asyncio.create_task(self.crawl()) for _ in range(concurrency)]

    async def join(self):
        await asyncio.gather(*self.producers)

    async def add_crawl(self, url: str):
        await self.link_queue.put((url, urlparse(url).path))

    async def crawl(self):
        async with ClientSession() as session:
            while True:
                root_url, path = await self.link_queue.get()

                full_url = urljoin(root_url, path)
                async with self.throttler:
                    async with session.get(full_url) as resp:
                        if resp.content_type.startswith('text/html'):
                            blob = await resp.read()

                            html_match = re.search(self.html_regex, blob, re.DOTALL)
                            title, body = html_match.group(1, 2)

                            matches = re.finditer(self.link_regex, body, re.MULTILINE | re.DOTALL)
                            for match in matches:
                                groups = match.groups()
                                link = urljoin(full_url, groups[0].decode())
                                path = urlparse(link).path

                                if urlparse(link).netloc == urlparse(root_url).netloc:
                                    self.link_queue.put_nowait((root_url, path))

                            self.article_queue.put_nowait(Article(title.decode(),
                                                                  root_url,
                                                                  full_url,
                                                                  self.h.handle(body.decode())))

                self.link_queue.task_done()