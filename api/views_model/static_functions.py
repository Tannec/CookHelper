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