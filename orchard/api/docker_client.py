import docker
import orchard
import websocket

from .utils import request_to_curl_command

import logging
log = logging.getLogger(__name__)

class DockerClient(docker.Client):
    def __init__(self, base_url, auth_token, *args, **kwargs):
        super(DockerClient, self).__init__(base_url, *args, **kwargs)

        self.auth_header = "Token %s" % auth_token
        self.headers["Authorization"] = self.auth_header
        self.headers["User-Agent"] = "orchard/%s" % orchard.__version__

        del self.headers["Accept-Encoding"]
        del self.headers["Accept"]

    def send(self, request, **kwargs):
        log.debug(request_to_curl_command(request))
        return super(DockerClient, self).send(request, **kwargs)

    def _create_websocket_connection(self, url):
        log.debug("Opening websocket connection to %s", url)

        socket = websocket.create_connection(
            url,
            timeout=None,
            header=["Authorization: %s" % self.auth_header]
        )

        log.debug("Opened")

        return socket

    def replace_container(self, container_id, config):
        u = self._url("/containers/create?replaceContainer={0}".format(container_id))
        return self._result(self._post_json(u, config), json=True)
