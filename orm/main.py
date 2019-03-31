import sqlite3
from models import User, Man
from orm.exceptions import DoesNotExistError


def main():
    with sqlite3.connect('database.sqlite') as conn:
        User.ensure_table(conn)
        Man.ensure_table(conn)

        user = User.objects.create(conn, id=1, name='user1')
        print('inserted user:', user)

        queried_user = User.objects.get(conn, pk=1)
        print('queried user:', queried_user, '\n')

        man = Man(id=1, name='man1', sex='m')
        man.save(conn)
        print('inserted man:', man)

        queried_man = Man.objects.get(conn, pk=1)
        print('queried man:', queried_man, '\n')

        man.sex = 'f'
        man.save(conn)
        print('updated man:', man)

        updated_man = Man.objects.get(conn, pk=1)
        print('queried man:', updated_man, '\n')


        man.delete(conn)
        try:
            del_man = Man.objects.get(conn, pk=1)
            print(del_man)
        except DoesNotExistError as e:
            print(e)


if __name__ == '__main__':
    main()
