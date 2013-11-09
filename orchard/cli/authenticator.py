import os
import hashlib
from getpass import getpass

from .. import api
from ..api.errors import AuthenticationFailed

from .errors import UserError
from .utils import mkdir

import logging
log = logging.getLogger(__name__)


class Authenticator(object):
    def __init__(self, token_dir):
        mkdir(token_dir)
        url_hash = hashlib.md5(api.base_url()).hexdigest()
        self.token_file = os.path.join(token_dir, url_hash)

    def authenticate(self):
        stored_token = self.load_token()

        if stored_token:
            try:
                return api.with_token(stored_token)
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
            self.store_token(client.token)
            return client
        except AuthenticationFailed:
            # TODO: pre-fill with previous value
            # http://stackoverflow.com/questions/2533120/show-default-value-for-editing-on-python-input-possible
            log.error("Sorry, that doesn't look right. Try again?")
            return self.login(prompt="Username: ")

    def load_token(self):
        if os.path.exists(self.token_file):
            return open(self.token_file).read().strip()

    def store_token(self, token):
        open(self.token_file, 'w').write(token)
