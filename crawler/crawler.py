import asyncio
import logging
import re
from asyncio import Queue, Event
from dataclasses import dataclass
from typing import Tuple
from urllib.parse import urljoin, urlparse

import html2text
from aiohttp import ClientSession
from asyncio_throttle import Throttler


@dataclass
class Article:
    title: str
    site: str
    url: str

    def __hash__(self) -> int:
        return hash(self.url)


class LinkQueue(Queue):
    def _init(self, maxsize: int) -> None:
        super()._init(maxsize)
        self._put_items = set()

    def put_nowait(self, item: Tuple[str, str]) -> None:
        root_url, url = item
        full_url = urljoin(root_url, url)
        if full_url not in self._put_items:
            self._put_items.add(full_url)
            super().put_nowait(item)


class Crawler:
    title_regex = b'<title.*?>(.*?)</title.*?>'
    link_regex = b'<a.+?href=\"(.+?)\".*?>.*?</a.*?>'

    def __init__(self, rate: int = 10, concurrency: int = 5, article_queue: Queue = None) -> None:
        self.h = html2text.HTML2Text()
        self.h.ignore_links = True

        self.throttler = Throttler(rate)

        self.concurrency = concurrency
        self.locked_coroutine_count = 0

        self.article_queue = article_queue or Queue()
        self.link_queue = LinkQueue()

        self.producers = [asyncio.create_task(self._crawl()) for _ in range(concurrency)]
        self.done = Event()

    async def join(self) -> None:
        await self.done.wait()
        for task in self.producers:
            task.cancel()

    async def add_crawl(self, url: str) -> None:
        await self.link_queue.put((url, urlparse(url).path))

    async def _crawl(self) -> None:
        async with ClientSession() as session:
            while True:
                self.locked_coroutine_count += 1
                if self.link_queue.empty() and self.locked_coroutine_count == self.concurrency:
                    self.done.set()

                root_url, path = await self.link_queue.get()
                self.locked_coroutine_count -= 1

                full_url = urljoin(root_url, path)
                async with self.throttler:
                    async with session.get(full_url, allow_redirects=False) as resp:
                        if resp.status != 200:
                            logging.error(f'error status: {resp.status}')
                            self.link_queue.task_done()
                            continue

                        if resp.content_type.startswith('text/html'):
                            blob = await resp.read()

                            title_match = re.search(self.title_regex, blob, re.IGNORECASE)
                            title = title_match.group(1) if title_match is not None else b''

                            for match in re.finditer(self.link_regex, blob, re.IGNORECASE | re.DOTALL):
                                groups = match.groups()
                                link = urljoin(full_url, groups[0].decode())
                                path = urlparse(link).path

                                if urlparse(link).netloc == urlparse(root_url).netloc:
                                    await self.link_queue.put((root_url, path))

                            self.article_queue.put_nowait(Article(
                                title=self.h.handle(title.decode()),
                                site=root_url,
                                url=full_url,
                            ))

                self.link_queue.task_done()
