from .resource import Model, Collection


class App(Model):
    attr_names = Model.attr_names + ['name']


class AppCollection(Collection):
    model = App
