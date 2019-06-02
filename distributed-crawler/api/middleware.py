from functools import wraps

from helpers import respond


class AuthMiddleware:
    def __init__(self, auth):
        self.auth = auth

    async def __call__(self, app, handler):
        async def middleware(request):
            request.user = None
            token = request.headers.get('X-Token', None)
            if token:
                user = await self.auth.validate(token=token)
                if user is None:
                    return respond({}, 'invalid token', 400)
                else:
                    request.user = user

            return await handler(request)

        return middleware


def login_required(handler):
    @wraps(handler)
    def wrapper(request):
        if not request.user:
            return respond({}, 'forbidden', 403)
        return handler(request)

    return wrapper
