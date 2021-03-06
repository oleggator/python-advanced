from orm.exceptions import DoesNotExistError

from copy import deepcopy


class QuerySet:
    def __init__(self, conn, models_cls):
        self.model_cls = models_cls
        self.conn = conn

        self.filtered_fields = {}

    def filter(self, *_, **fields) -> 'QuerySet':
        for k, v in fields.items():
            self.filtered_fields[k] = v

        return self

    def evaluate(self):
        fields = []
        values = []
        for k, v in self.filtered_fields.items():
            fields.append(f'{k} = ?')
            validated_value = getattr(self.model_cls, k).validate(v)
            values.append(validated_value)

        table_name = self.model_cls._table_name
        field_names = self.model_cls.get_field_names()
        field_names_string = ', '.join(field_names)
        where_fields_string = f'where {", ".join(fields)}'

        query = f'select {field_names_string} from {table_name} {where_fields_string}'
        cursor = self.conn.cursor()
        cursor.execute(query, values)

        tuples = []
        for row in cursor.fetchall():
            field_values = dict(zip(field_names, row))
            tuples.append(self.model_cls(**field_values))

        return tuples

    def create(self, *args, **kwargs):
        obj = self.model_cls(*args, **kwargs)
        obj.save(self.conn)

        return obj

    def delete(self):
        fields = []
        values = []
        for k, v in self.filtered_fields.items():
            fields.append(f'{k} = ?')
            validated_value = getattr(self.model_cls, k).validate(v)
            values.append(validated_value)

        table_name = self.model_cls._table_name
        where_fields_string = f'where {", ".join(fields)}'

        query = f'delete from {table_name} {where_fields_string}'
        cursor = self.conn.cursor()
        cursor.execute(query, values)

        self.conn.commit()

    def get(self, pk):
        pk_name = self.model_cls.pk_field_name
        pk_validated = getattr(self.model_cls, pk_name).validate(pk)
        result = self.filter(**{pk_name: pk_validated}).evaluate()
        if len(result) == 0:
            raise DoesNotExistError(f'{self.model_cls.__name__} with {pk_name}={pk_validated} does not exists')
        return result[0]

    def all(self):
        return deepcopy(self)

    def __iter__(self):
        return iter(self.evaluate())
