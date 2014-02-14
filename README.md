Orchard Python client
=====================

This package provides Python bindings for [Orchard], letting you manage Docker hosts for a particular account and interact with an individual host using [docker-py].

Install
-------

```bash
$ pip install orchard
```

Authenticating
--------------

The `orchard` package provides two methods for instantiating an API client:

```python
>>> import orchard
>>> orchard.with_token(my_token)
<orchard.client.Client object at 0x101de0d10>
>>> orchard.with_username_and_password(my_username, my_password)
<orchard.client.Client object at 0x102244e10>
```

Managing hosts
--------------

Once you've instaniated a `Client` object, the `hosts` property lets you list, create and delete hosts:

```python
>>> client.hosts
[<Host: default>, <Host: host2>]
>>> client.hosts[0]
<Host: default>
>>> client.hosts["host2"]
<Host: host2>
>>> host3 = client.hosts.create({"name": "host3"})
>>> host3
<Host: host3>
>>> host3.delete()
```

Interacting with Docker
-----------------------

To get a [docker-py] instance for a host, call `host.docker()`:

```python
>>> docker = client.hosts["default"].docker()
>>> docker.containers()
[]
>>> c = docker.create_container("ubuntu", "date")
>>> docker.start(c['Id'])
>>> docker.wait(c['Id'])
0
>>> docker.logs(c['Id'])
'Mon Oct 28 15:42:56 UTC 2013\n'
>>> docker.remove_container(c['Id'])
```

See the [docker-py] README for a full list of methods.

[Orchard]: https://orchardup.com
[docker-py]: https://github.com/dotcloud/docker-py
[CLI docs]: https://orchardup.com/docs/cli
[Orchard API docs]: https://orchardup.com/docs/api
