import logging
import requests
import orchard
import urlparse

from .docker_client import DockerClient
from .models.app import AppCollection
from .errors import HTTPError
from .utils import request_to_curl_command

log = logging.getLogger(__name__)

class Client(object):
    def __init__(self, base_url, docker_host):
        if base_url.endswith("/"):
            base_url = base_url[:-1]

        self.base_url = base_url
        self.docker_host = docker_host

    @property
    def apps(self):
        return AppCollection(client=self, url="/apps")

    def customer_data(self):
        return self.request("GET", "/customers/me")

    def docker(self, app_name):
        docker_url = self.docker_host % app_name

        log.debug("Connecting to Docker API at %s", docker_url)
        return DockerClient(base_url=docker_url, auth_token=self.token, version="1.5")

    def request(self, method, path_or_url, quiet=False, headers=None, **kwargs):
        if headers is None:
            headers = {}

        url = self.build_url(path_or_url)

        if hasattr(self, 'token'):
            headers["Authorization"] = "Token %s" % self.token
            headers["User-Agent"] = "orchard/%s" % orchard.__version__

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


