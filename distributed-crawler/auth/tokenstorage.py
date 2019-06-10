from datetime import datetime, timedelta
from uuid import uuid4

from models import Users, Tokens, CrawlerStats


class TokenStorage:
    def __init__(self, db_conn):
        self.db_conn = db_conn

    async def signup(self, *, email, password, name):
        user = await Users.objects.create(self.db_conn,
                                          name=name,
                                          email=email,
                                          password=password,
                                          created_date=datetime.now(),
                                          last_login_date=datetime.now())

        return user.__dict__

    async def login(self, *, email, password):
        users = await Users.objects.filter(self.db_conn, email=email, password=password).evaluate()
        if len(users) < 1:
            return None

        user = users[0]
        expire_date = datetime.now() + timedelta(days=30)
        token = await Tokens.objects.create(self.db_conn,
                                            user_id=user.id,
                                            token=str(uuid4()),
                                            expire_date=expire_date)

        return token.__dict__

    async def validate(self, *, token):
        tokens = await Tokens.objects.filter(self.db_conn, token=token).evaluate()
        if len(tokens) < 1:
            return None

        token = tokens[0]
        if token.expire_date <= datetime.now():
            return None

        user = await Users.objects.get(self.db_conn, pk=token.user_id)

        return user.__dict__

    async def expire(self, *, token):
        tokens = await Tokens.objects.filter(self.db_conn, token=token).evaluate()
        if len(token) < 1:
            return None

        token = tokens[0]
        token.expire_date = datetime.now()
        await token.save()

        return token.__dict__
