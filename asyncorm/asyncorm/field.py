from datetime import datetime

from .exceptions import FieldError


class Field:
    def __init__(self, f_type, required=True, default=None, primary_key=False):
        self.f_type = f_type
        self.required = required
        self.default = default
        self.primary_key = primary_key

    def validate(self, value):
        if value is None and not self.required and not self.default:
            raise FieldError('required field is empty')

        if value is None and self.default is not None:
            return value

        if type(value) != self.f_type:
            raise FieldError(f'wrong value type: {type(value)} != {self.f_type}')

        return value


class IntegerField(Field):
    type = 'integer'

    def __init__(self, required=True, default=None, primary_key=False):
        super().__init__(int, required, default, primary_key)


class TextField(Field):
    type = 'text'

    def __init__(self, required=True, default=None, primary_key=False):
        super().__init__(str, required, default, primary_key)


class RealField(Field):
    type = 'real'

    def __init__(self, required=True, default=None, primary_key=False):
        super().__init__(float, required, default, primary_key)


class DateTimeField(Field):
    type = 'timestamp'

    def __init__(self, required=True, default=None, primary_key=False):
        super().__init__(datetime, required, default, primary_key)
