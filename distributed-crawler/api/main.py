from os import getenv

from aio_pika import connect_robust
from aio_pika.patterns import RPC
from aioelasticsearch import Elasticsearch
from aiohttp import web

from middleware import AuthMiddleware
from handlers import search, signup, login, get_current_user, index, get_statistic

es_endpoint = getenv('ES_ENDPOINT', 'http://elasticsearch:9200')
amqp_endpoint = getenv('AMQP_ENDPOINT', 'amqp://guest:guest@broker/')


async def main():
    connection = await connect_robust(amqp_endpoint)
    channel = await connection.channel()
    auth_rpc = await RPC.create(channel)

    auth_middleware = AuthMiddleware(auth_rpc.proxy)
    app = web.Application(middlewares=[auth_middleware])

    app.add_routes([
        web.post('/api/v1/signup', signup),
        web.post('/api/v1/login', login),
        web.get('/api/v1/search', search),

        web.get('/api/v1/current', get_current_user),
        web.post('/api/v1/index', index),
        web.get('/api/v1/stat', get_statistic),
    ])

    app.es = Elasticsearch(es_endpoint)
    app.auth = auth_rpc.proxy

    return app


if __name__ == '__main__':
    web.run_app(main())
