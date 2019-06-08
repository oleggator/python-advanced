import asyncio

import asyncpg
import yaml
from aio_pika import connect_robust
from aio_pika.patterns import RPC

from models import Users, Tokens, CrawlerStats
from tokenstorage import TokenStorage


async def main():
    with open('config.yml', 'r') as config_file:
        config = yaml.load(config_file)

    amqp_endpoint = config.get('amqp_endpoint', 'amqp://guest:guest@broker/')
    postgres_user = config.get('postgres_user', 'postgres')
    postgres_password = config.get('postgres_password', 'postgres')
    postgres_db = config.get('postgres_db', 'postgres')
    postgres_host = config.get('postgres_host', 'postgres')

    connection = await connect_robust(amqp_endpoint)

    db_conn = await asyncpg.connect(user=postgres_user, password=postgres_password,
                                    database=postgres_db, host=postgres_host)

    await Users.ensure_table(db_conn)
    await Tokens.ensure_table(db_conn)
    await CrawlerStats.ensure_table(db_conn)
    token_storage = TokenStorage(db_conn)

    channel = await connection.channel()
    rpc = await RPC.create(channel)
    await rpc.register('signup', token_storage.signup, auto_delete=True)
    await rpc.register('login', token_storage.login, auto_delete=True)
    await rpc.register('validate', token_storage.validate, auto_delete=True)
    await rpc.register('expire', token_storage.expire, auto_delete=True)

    return connection


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    conn = loop.run_until_complete(main())

    try:
        loop.run_forever()
    finally:
        loop.run_until_complete(conn.close())
        loop.shutdown_asyncgens()
