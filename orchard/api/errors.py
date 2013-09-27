class HTTPError(Exception):
    def __init__(self, status, json=None):
        self.status = status
        self.json = json

    @staticmethod
    def for_status(status, json=None):
        if status in range(400, 499):
            return ClientError.for_status(status, json)
        elif status in range(500, 599):
            return ServerError.for_status(status, json)
        else:
            return HTTPError(status, json)


class ClientError(HTTPError):
    @staticmethod
    def for_status(status, json=None):
        if status == 400:
            return BadRequest(status, json)
        elif status == 401:
            return Unauthorized(status, json)
        elif status == 403:
            return Forbidden(status, json)
        elif status == 404:
            return NotFound(status, json)
        else:
            return ClientError(status, json)


class BadRequest(ClientError):
    pass


class Unauthorized(ClientError):
    pass


class Forbidden(ClientError):
    pass


class NotFound(ClientError):
    pass


class ServerError(HTTPError):
    @staticmethod
    def for_status(status, json=None):
        return ServerError(status, json)


class AuthenticationFailed(Exception):
    pass
