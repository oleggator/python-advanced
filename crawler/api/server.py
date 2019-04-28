from aioelasticsearch import Elasticsearch
from aiohttp import web


async def handle(request: web.Request):
    if 'q' not in request.rel_url.query:
        return web.Response(status=400)
    query = request.rel_url.query['q']

    limit = 10
    if 'limit' in request.rel_url.query:
        limit = request.rel_url.query['limit']

    offset = 0
    if 'offset' in request.rel_url.query:
        offset = request.rel_url.query['offset']

    async with Elasticsearch() as es:
        resp = await es.search('sites', '_doc', q=query, from_=offset, size=limit)

        hits = sorted(resp['hits']['hits'], key=lambda hit: hit['_score'], reverse=True)
        urls = [doc['_source']['url'] for doc in hits]

        return web.json_response(urls)


if __name__ == '__main__':
    app = web.Application()
    app.add_routes([web.get('/api/v1/search', handle)])
    web.run_app(app)
