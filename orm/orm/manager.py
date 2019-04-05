from sqlite3 import Cursor

from .exceptions import DoesNotExistError


class Manager:
    def __init__(self):
        self.model_cls = None

    def __get__(self, instance, owner):
        self.model_cls = owner

        return self

    def create(self, conn, *args, **kwargs):
        obj = self.model_cls(*args, **kwargs)
        obj.save(conn)

        return obj

    def get(self, conn, pk):
        pk_name = self.model_cls.pk_field_name
        table_name = self.model_cls._table_name
        field_names = self.model_cls.get_field_names()
        field_names_string = ', '.join(field_names)

        pk_validated = getattr(self.model_cls, pk_name).validate(pk)

        query = f'select {field_names_string} from {table_name} where {pk_name} = ?'
        cursor: Cursor = conn.cursor()
        cursor.execute(query, (pk_validated,))

        result = cursor.fetchone()
        if result is None:
            raise DoesNotExistError(f'{self.model_cls.__name__} with {pk_name}={pk_validated} does not exists')

        field_values = dict(zip(field_names, result))
        return self.model_cls(**field_values)

    def filter(self, conn, **kwargs):
        fields = []
        values = []
        for k, v in kwargs.items():
            fields.append(f'{k} = ?')
            validated_value = getattr(self.model_cls, k).validate(v)
            values.append(validated_value)

        table_name = self.model_cls._table_name
        field_names = self.model_cls.get_field_names()
        field_names_string = ', '.join(field_names)
        where_fields_string = ', '.join(fields)

        query = f'select {field_names_string} from {table_name} where {where_fields_string}'
        cursor: Cursor = conn.cursor()
        cursor.execute(query, values)

        users = []
        for row in cursor.fetchall():
            field_values = dict(zip(field_names, row))
            users.append(self.model_cls(**field_values))

        return users
