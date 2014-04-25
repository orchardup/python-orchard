import os

from .client import Client
from .errors import BadRequest, AuthenticationFailed

__version__ = '2.0.1'

def with_token(token):
    client = Client(base_url())
    client.token = token
    return client


def with_username_and_password(username, password):
    client = Client(base_url())

    try:
        client.token = client.request("POST", "/signin", data={"username": username, "password": password}, quiet=True)["token"]
        return client
    except BadRequest:
        raise AuthenticationFailed()


def base_url():
    return os.environ.get('ORCHARD_API_URL', 'https://api.orchardup.com/v2')
