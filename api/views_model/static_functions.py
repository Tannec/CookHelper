class FieldRequiredException(Exception):
    field = 'Missed some field'

    def __init__(self, field='some field'):
        super(FieldRequiredException, self).__init__()
        self.field = field.capitalize()

    def __str__(self):
        return f'{self.field} required'

    def __int__(self):
        return 104


class UnknownField(Exception):

    def __init__(self, field='unknown field'):
        super().__init__()
        self.field = field

    def __str__(self):
        return 'Wrong field detected'

    def __int__(self):
        return 199

    def unknownField(self):
        return self.field


class MissFields(Exception):
    def __init__(self, elems=''):
        super().__init__()
        self.fields = elems

    def __str__(self):
        return 'Missed some fields'

    def __int__(self):
        return 104

    def missedFields(self):
        return ", ".join(self.fields)


class RejectException(Exception):
    field = 'some field'
    status = 110

    def __init__(self, field='some field', status=110):
        super(RejectException, self).__init__()
        self.field = field.capitalize
        self.status = status

    def __str__(self):
        return f'{self.field} rejected'

    def __int__(self):
        return self.status


class PermissionException(Exception):
    def __init__(self):
        super(PermissionException, self).__init__()

    def __str__(self):
        return 'Permission denied'

    def __int__(self):
        return 106


class ModelException(Exception):
    message = 'Exception'
    status = -1

    def __init__(self, message='', status=-1):
        super(ModelException, self).__init__()
        self.status = status
        self.message = message

    def __str__(self):
        return self.message

    def __int__(self):
        return self.status


class SuccessException(Exception):
    message = 'Success'
    status = 100

    def __init__(self, message='', status=100):
        super(ModelException, self).__init__()
        self.status = status
        self.message = message

    def __str__(self):
        return self.message

    def __int__(self):
        return self.status


def clear(field):
    data = field
    if type(data) is dict:
        for i in data:
            data[i] = clear(data[i])
    elif data is None:
        return None
    else:
        if data[0] == data[-1] == '"':
            data = data[1: len(data) - 1]
    return data
