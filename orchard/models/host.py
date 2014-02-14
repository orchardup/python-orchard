from ..docker_client import DockerClient
from .resource import Model, Collection
import os


class Host(Model):
    attr_names = Model.attr_names + ['name', 'size', 'ipv4_address', 'client_key', 'client_cert']

    def docker(self):
        self._store_certs()
        return DockerClient(
            base_url='https://%s:4243' % self.ipv4_address,
            verify=self._host_ca_path(),
            cert=(self._client_cert_path(), self._client_key_path()),
        )

    def _store_certs(self):
        if not os.path.exists(self._keys_path()):
            os.makedirs(self._keys_path())
        os.chmod(self._keys_path(), 0700)
        with open(self._client_key_path(), 'w') as fh:
            fh.write(self.client_key)
        with open(self._client_cert_path(), 'w') as fh:
            fh.write(self.client_cert)

    def _keys_path(self):
        return os.path.expanduser('~/.orchard/host-keys')

    def _host_ca_path(self):
        return os.path.abspath(os.path.join(os.path.dirname(__file__), '../certs/host-ca.pem'))

    def _client_key_path(self):
        return os.path.join(self._keys_path(), '%s.key' % self.id)

    def _client_cert_path(self):
        return os.path.join(self._keys_path(), '%s.crt' % self.id)

class HostCollection(Collection):
    model = Host
