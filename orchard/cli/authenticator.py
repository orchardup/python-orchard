import os
import hashlib
import json
from getpass import getpass

from .. import api
from ..api.errors import AuthenticationFailed

from .utils import mkdir

import logging
log = logging.getLogger(__name__)


class Authenticator(object):
    def __init__(self, token_dir):
        mkdir(token_dir)
        url_hash = hashlib.md5(api.base_url()).hexdigest()
        self.token_file = os.path.join(token_dir, url_hash)

    def authenticate(self):
        if 'ORCHARD_API_KEY' in os.environ:
            client = api.with_token(os.environ['ORCHARD_API_KEY'])
            client.username = client.customer_data()["username"]
            return client

        loaded_data = self.load_user_data()

        if loaded_data:
            try:
                client = api.with_token(loaded_data["token"])

                if "username" not in loaded_data:
                    log.debug("Found API token but no other data - requesting")
                    extra_data = client.customer_data()
                    loaded_data.update(extra_data)
                    self.store_user_data(loaded_data)

                client.username = loaded_data["username"]

                return client
            except AuthenticationFailed:
                log.error("Oh dear, looks like your API token has expired. We'll need to log you in again.")

        return self.login()

    def login(self, prompt=None):
        if prompt is None:
            prompt = 'Orchard username: '

        username = raw_input(prompt)

        try:
            password = getpass('Password: ')
            client = api.with_username_and_password(username, password)
            client.username = username
            self.store_user_data(client.customer_data())
            return client
        except AuthenticationFailed:
            # TODO: pre-fill with previous value
            # http://stackoverflow.com/questions/2533120/show-default-value-for-editing-on-python-input-possible
            log.error("Sorry, that doesn't look right. Try again?")
            return self.login(prompt="Username: ")

    def load_user_data(self):
        if not os.path.exists(self.token_file):
            return None

        raw_data = open(self.token_file).read()

        try:
            return json.loads(raw_data)
        except ValueError:
            return {"token": raw_data.strip()}

    def store_user_data(self, data):
        open(self.token_file, 'w').write(json.dumps(data))
