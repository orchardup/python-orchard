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

    >>> docker.containers()
    []

    >>> c = docker.create_container("ubuntu", "date")

    >>> docker.start(c['Id'])
    
    >>> docker.wait(c['Id'])
    0

    >>> docker.logs(c['Id'])
    'Mon Oct 28 15:42:56 UTC 2013\n'
    
    >>> docker.remove_container(c['Id'])

Consult the [docker-py] README for a full list of methods. Orchard does not currently support all of the methods that Docker supports though. See the [Orchard API docs] for a list of what is not supported.

[Orchard]: https://orchardup.com
[docker-py]: https://github.com/dotcloud/docker-py
[CLI docs]: https://orchardup.com/docs/cli
[Orchard API docs]: https://orchardup.com/docs/api
