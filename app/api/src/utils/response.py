def _respond(status, data, status_code):
    response = {
        'status': status,
        'data': data
    }
    return response, status_code


def success(data):
    return _respond('success', data, 200)


def failure(data, status_code):
    return _respond('failure', data, status_code)