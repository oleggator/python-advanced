from orm.model import Model
from orm.field import IntegerField, TextField


class User(Model):
    id = IntegerField(primary_key=True)
    name = TextField(default='default user name')

    class Meta:
        table_name = 'User'


class Man(User):
    sex = TextField()

    class Meta:
        table_name = 'Man'
