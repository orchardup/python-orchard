Orchard Python client
=====================

This package provides both a command-line and Python client for [Orchard]. Both provide functionality for managing Orchard apps under an account and for interacting with an individual app's Docker instance using [docker-py].

Install
-------

    $ pip install orchard

Command-line client
-------------------

For help on using Orchard from the command-line, run `orchard --help` or see the [CLI docs] on the website.

Authenticating
--------------

The `orchard.api` package provides two methods for instantiating an API client:

    >>> import orchard.api

    >>> orchard.api.with_token(my_token)
    <orchard.api.client.Client object at 0x101de0d10>

    >>> orchard.api.with_username_and_password(my_username, my_password)
    <orchard.api.client.Client object at 0x102244e10>

Managing apps
-------------

Once you've instaniated a `Client` object, the `apps` property lets you list, create and delete apps:

    >>> client.apps
    [<App: app1>, <App: app2>]

    >>> client.apps[0]
    <App: app1>

    >>> client.apps["app2"]
    <App: app2>

    >>> app3 = client.apps.create({"name": "app3"})

    >>> app3
    <App: app3>

    >>> app3.delete()

Interacting with Docker
-----------------------

To get a [docker-py] instance for an app, call `client.docker(app_name)`:

    >>> docker = client.docker("app1")

    >>> docker
    <orchard.api.docker_client.DockerClient object at 0x1022a4e50>

    >>> docker.containers()
    []

    >>> c = docker.create_container("ubuntu", "touch /file.txt")

    >>> docker.inspect_container(c['Id'])
    {
        u'ID': u'8d1ade26b2b50026a74a5bc55dbe9131fdbd17b1311b512568913e9b84f01209',
        u'Image': u'8dbd9e392a964056420e5d58ca5cc376ef18e2de93b5cc90e868a1bbc8318c1c',
        u'Path': u'touch',
        u'Args': [u'/file.txt'],
        u'State': {...},
        u'Config': {...},
        u'NetworkSettings': {...},
        ...
    }

    >>> docker.start(c['Id'])

    >>> docker.diff(c['Id'])
    [
        {u'Path': u'/dev', u'Kind': 0},
        {u'Path': u'/dev/kmsg', u'Kind': 1},
        {u'Path': u'/file.txt', u'Kind': 1}
    ]

Consult the [docker-py] README for a full list of methods.

[Orchard]: https://orchardup.com
[docker-py]: https://github.com/dotcloud/docker-py
[CLI docs]: https://orchardup.com/docs/cli
