import logging

from aioelasticsearch import Elasticsearch
from aiohttp.abc import Request
from aiohttp.web_response import Response

from middleware import login_required
from helpers import respond

INDEX_NAME = 'sites'


async def search(request: Request) -> Response:
    if 'q' not in request.rel_url.query:
        return respond({}, 'query is empty', 400)
    query = request.rel_url.query['q']

    limit = 10
    if 'limit' in request.rel_url.query:
        if not request.rel_url.query['limit'].isdigit():
            return respond({}, "parameter 'limit' must be integer", 400)

        limit = int(request.rel_url.query['limit'])

    offset = 0
    if 'offset' in request.rel_url.query:
        if not request.rel_url.query['offset'].isdigit():
            return respond({}, "parameter 'offset' must be integer", 400)

        offset = int(request.rel_url.query['offset'])

    es: Elasticsearch = request.app.es
    if not await es.indices.exists(INDEX_NAME):
        return respond({}, f"there is no index '{INDEX_NAME}'", 404)

    resp = await es.search('sites', '_doc', q=query, from_=offset, size=limit, sort='_score:desc')
    urls = [doc['_source']['url'] for doc in resp['hits']['hits']]

    return respond(urls)


async def login(request: Request) -> Response:
    post = await request.post()

    email = post.get('email')
    if email is None:
        respond({}, 'email field is required', 400)

    password = post.get('password')
    if password is None:
        respond({}, 'password field is required', 400)

    auth = request.app.auth
    token = await auth.login(email=email, password=password)
    return respond(token)


async def signup(request: Request) -> Response:
    post = await request.post()

    email = post.get('email')
    if email is None:
        respond({}, 'email field is required', 400)

    password = post.get('password')
    if password is None:
        respond({}, 'password field is required', 400)

    name = post.get('name')
    if name is None:
        respond({}, 'name field is required', 400)

    auth = request.app.auth
    user = await auth.signup(email=email, password=password, name=name)
    return respond(user)


@login_required
async def get_current_user(request: Request) -> Response:
    user = request.user
    return respond(user)


@login_required
async def index(request: Request) -> Response:
    post = await request.post()

    domain = post.get('domain')
    if domain is None:
        respond({}, 'domain field is required', 400)

    https = post.get('https')
    if https is None:
        respond({}, 'domain field is required', 400)

    await request.app.index(domain=domain, https=https)
    return respond('queued')


@login_required
async def get_statistic(request: Request) -> Response:
    return respond('not implemented')
