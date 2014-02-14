from ..errors import ClientError


class Model(object):
    attr_names = ['id', 'url']

    def __init__(self, attrs={}, url=None, client=None, collection=None):
        self.url = url
        self.client = client
        self.collection = collection
        self.set(attrs)

    def __eq__(self, other):
        return type(self) == type(other) and self.attrs == other.attrs

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self.attrs.get("name"))

    def set(self, attrs):
        self.attrs = attrs

        for name in self.attr_names:
            if name in self.attrs:
                setattr(self, name, self.attrs[name])

    def update(self, attrs):
        attrs = self.client.request("PATCH", self.url, data=attrs)
        self.set(attrs)

    def delete(self):
        self.collection.delete(self)


class Collection(object):
    def __init__(self, models=None, client=None, url=None):
        self._models = None
        self.client = client
        self.url = url

        if models:
            self.reset(models)

    @property
    def models(self):
        if self._models is None:
            self.fetch()

        return self._models

    def reset(self, models):
        self._models = map(self.prepare_model, models)

    def fetch(self):
        if self.url:
            self.reset(self.client.request("GET", self.url))
        else:
            raise Exception("fetch() called on %s, but it has no url" % self.__class__.__name__)

    def get(self, key):
        return self.prepare_model(self.client.request("GET", "%s/%s" % (self.url, key)))

    def create(self, attrs=None):
        return self.prepare_model(self.client.request("POST", self.url, data=attrs))

    def delete(self, model):
        self.client.request("DELETE", model.url)

        if self._models:
            self._models.remove(model)

    def prepare_model(self, attrs):
        if isinstance(attrs, Model):
            attrs.client = self.client
            attrs.collection = self
            return attrs
        elif isinstance(attrs, dict):
            return self.model(attrs=attrs, client=self.client, collection=self)
        else:
            raise Exception("Can't create %s from %s" % (self.model.__name__, attrs))

    def __eq__(self, other):
        if isinstance(other, Collection):
            return self.models == other.models
        else:
            return self.models == other

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.models[key]
        else:
            return self.get(key)

    def __repr__(self):
        return str(self.models)

    def __len__(self):
        return len(self.models)
