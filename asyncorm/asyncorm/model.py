from numbers import Number
from sqlite3 import Connection

from .exceptions import ORMError
from .field import Field
from .manager import Manager


class ModelMeta(type):
    def __new__(mcs, name, bases, namespace):
        if name == 'Model':
            return super().__new__(mcs, name, bases, namespace)

        fields = {}
        pk_field_name = None
        for base in bases:
            if base is not Model and issubclass(base, Model):
                namespace['_table_name'] = base.Meta.table_name
                pk_field_name = base.pk_field_name
                for k, v in base._fields.items():
                    fields[k] = v

        meta = namespace.get('Meta')
        if meta:
            if hasattr(meta, 'table_name'):
                namespace['_table_name'] = meta.table_name
            elif '_table_name' not in namespace:
                raise ValueError('table_name is empty')
        elif '_table_name' not in namespace:
            raise ValueError('meta is none')

        for k, v in namespace.items():
            if isinstance(v, Field):
                fields[k] = v
                if v.primary_key:
                    if pk_field_name is None:
                        pk_field_name = k
                    else:
                        raise RuntimeError('more than one pk')
        if pk_field_name is None:
            raise ORMError('primary key required')

        namespace['pk_field_name'] = pk_field_name
        namespace['_fields'] = fields

        return super().__new__(mcs, name, bases, namespace)


class Model(metaclass=ModelMeta):
    class Meta:
        table_name = ''

    objects: Manager = Manager()

    def __init__(self, *_, **kwargs):
        for field_name, field in self._fields.items():
            value = field.validate(kwargs.get(field_name))
            setattr(self, field_name, value)

        if not hasattr(self, 'pk_field_name'):
            raise ORMError('primary key required')

    async def save(self, db_conn: Connection):
        field_names = self.get_field_names()
        field_values = tuple(getattr(self, field_name) for field_name in field_names)

        field_names_string = ', '.join(field_names)
        values_string = ', '.join([f'${i+1}' for i in range(len(field_names))])
        updates = ', '.join([f'{field_names[i]} = ${i + 1 + len(field_names)}' for i in range(len(field_names))])

        query = f'''
            INSERT INTO {self.Meta.table_name} ({field_names_string})
            VALUES ({values_string})
            ON CONFLICT ({self.pk_field_name}) DO UPDATE SET {updates}
        '''
        await db_conn.execute(query, *field_values, *field_values)

    def delete(self, db_conn: Connection):
        query = f'DELETE FROM {self.Meta.table_name} WHERE {self.pk_field_name}=?'
        cursor = db_conn.cursor()
        cursor.execute(query, (getattr(self, self.pk_field_name),))

    @classmethod
    async def ensure_table(cls, db_conn: Connection):
        fields_string = ', '.join(cls.get_fields_sql_repr())
        query = f'CREATE TABLE IF NOT EXISTS {cls.Meta.table_name} ({fields_string})'
        await db_conn.execute(query)

    @classmethod
    def get_field_names(cls):
        return list(cls._fields.keys())

    @classmethod
    def get_fields_sql_repr(cls):
        field_strings = []
        for field_name, field in cls._fields.items():
            primary_key = 'PRIMARY KEY' if field.primary_key else ''
            required = 'NOT NULL' if field.required else ''

            default = ''
            if field.default is not None:
                default_string = field.default if isinstance(field.default, Number) else f"'{field.default}'"
                default = f'DEFAULT {default_string}' if field.default is not None else ''

            field_string = f'{field_name} {field.type} {primary_key} {required} {default}'
            field_strings.append(field_string)

        return field_strings

    def __str__(self):
        return str(vars(self))
