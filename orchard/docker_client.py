from .packages import docker
import os.path

class DockerClient(docker.Client):
    def __init__(self, base_url, verify, cert, *args, **kwargs):
        super(DockerClient, self).__init__(base_url, *args, **kwargs)
        self.verify = verify
        self.cert = cert
