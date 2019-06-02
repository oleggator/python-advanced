from .queryset import QuerySet


class Manager:
    def __init__(self):
        self.model_cls = None

    def __get__(self, instance, owner):
        self.model_cls = owner

        return self

    async def create(self, conn, *args, **kwargs):
        return await QuerySet(conn, self.model_cls).create(*args, **kwargs)

    async def get(self, conn, pk):
        return await QuerySet(conn, self.model_cls).get(pk)

    def filter(self, conn, **kwargs):
        return QuerySet(conn, self.model_cls).filter(**kwargs)

    def all(self, conn):
        return QuerySet(conn, self.model_cls)
