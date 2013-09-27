import logging
import os

from .docopt_command import DocoptCommand
from .authenticator import Authenticator
from .formatter import Formatter
from .utils import cached_property, mkdir

log = logging.getLogger(__name__)

class Command(DocoptCommand):
    @cached_property
    def api(self):
        token_dir = os.path.join(self.global_working_dir, 'api_tokens')
        authenticator = Authenticator(token_dir=token_dir)
        return authenticator.authenticate()

    @cached_property
    def formatter(self):
        return Formatter()

    @cached_property
    def global_working_dir(self):
        return mkdir(os.path.expanduser('~/.orchard'))
