from os import getenv

from aioelasticsearch import Elasticsearch
from aiohttp import web

es_endpoint = getenv('ES_ENDPOINT')
INDEX_NAME = 'sites'

def error(message: str, status: int):
    return web.json_response({ 'error': message }, status=status)

def payload(payload: str, status: int = 200):
    return web.json_response({ 'payload': payload }, status=status)

async def handle(request: web.Request):
    if 'q' not in request.rel_url.query:
        return error('query is empty', 400)
    query = request.rel_url.query['q']

    limit = 10
    if 'limit' in request.rel_url.query:
        if not request.rel_url.query['limit'].isdigit():
            return error("parameter 'limit' must be integer", 400)

        limit = int(request.rel_url.query['limit'])

    offset = 0
    if 'offset' in request.rel_url.query:
        if not request.rel_url.query['offset'].isdigit():
            return error("parameter 'offset' must be integer", 400)

        offset = int(request.rel_url.query['offset'])

    async with Elasticsearch(es_endpoint) as es:
        if not await es.indices.exists(INDEX_NAME):
            return error(f"there is no index '{INDEX_NAME}'", 404)

        resp = await es.search('sites', '_doc', q=query, from_=offset, size=limit, sort='_score:desc')
        urls = [doc['_source']['url'] for doc in resp['hits']['hits']]

        return payload(urls)


if __name__ == '__main__':
    app = web.Application()
    app.add_routes([web.get('/api/v1/search', handle)])
    web.run_app(app)
