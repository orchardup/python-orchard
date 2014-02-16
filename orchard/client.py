import logging
import requests
import orchard
import urlparse

from .models.host import HostCollection
from .errors import HTTPError
from .utils import request_to_curl_command

log = logging.getLogger(__name__)

class Client(object):
    def __init__(self, base_url):
        if base_url.endswith("/"):
            base_url = base_url[:-1]

        self.base_url = base_url

    @property
    def hosts(self):
        return HostCollection(client=self, url="/hosts")

    def customer_data(self):
        return self.request("GET", "/customers/me")

    def request(self, method, path_or_url, quiet=False, headers=None, **kwargs):
        if headers is None:
            headers = {}

        url = self.build_url(path_or_url)

        if hasattr(self, 'token'):
            headers["Authorization"] = "Token %s" % self.token
            headers["User-Agent"] = "python-orchard/%s" % orchard.__version__

        req = requests.Request(method, url, headers=headers, **kwargs).prepare()

        if not quiet:
            log.debug(request_to_curl_command(req))

        res = requests.sessions.Session().send(req)

        if not quiet:
            log.debug('%s %s' % (res.status_code, res.text))

        json = None
        try:
            json = res.json()
        except ValueError:
            pass

        try:
            res.raise_for_status()
        except requests.exceptions.HTTPError, e:
            raise HTTPError.for_status(e.response.status_code, json=json)

        return json

    def build_url(self, path_or_url):
        if '://' in path_or_url:
            return path_or_url

        if path_or_url.endswith("/"):
            path_or_url = path_or_url[:-1]

        components = urlparse.urlparse(self.base_url)
        components = (
            components.scheme,
            components.netloc,
            components.path + path_or_url,
            components.params,
            components.query,
            components.fragment)
        return urlparse.urlunparse(components)


