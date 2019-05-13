from os import getenv

from aioelasticsearch import Elasticsearch
from aiohttp import web

es_endpoint = getenv('ES_ENDPOINT')
INDEX_NAME = 'sites'


async def handle(request: web.Request):
    if 'q' not in request.rel_url.query:
        return web.json_response({
            'error': 'query is empty',
        }, status=400)
    query = request.rel_url.query['q']

    limit = 10
    if 'limit' in request.rel_url.query:
        limit = request.rel_url.query['limit']

    offset = 0
    if 'offset' in request.rel_url.query:
        offset = request.rel_url.query['offset']

    async with Elasticsearch(es_endpoint) as es:
        if not await es.indices.exists(INDEX_NAME):
            return web.json_response({
                'error': f"there is no index '{INDEX_NAME}'",
            }, status=404)

        resp = await es.search('sites', '_doc', q=query, from_=offset, size=limit, sort='_score:desc')
        urls = [doc['_source']['url'] for doc in resp['hits']['hits']]

        return web.json_response({
            'payload': urls,
        })


if __name__ == '__main__':
    app = web.Application()
    app.add_routes([web.get('/api/v1/search', handle)])
    web.run_app(app)
