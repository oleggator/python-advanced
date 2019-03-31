class ORMError(Exception):
    pass


class FieldError(ORMError):
    pass


class DoesNotExistError(ORMError):
    pass
