Change log
==========

2.0.0 (2014-02-16)
------------------

This package is no longer a CLI for Orchard – that has moved to the [Go client](https://github.com/orchardup/go-orchard).

 - Updated API to version 2. This removes containers and moves apps to hosts.
 - Moved `orchard.api` to the top level `orchard` package.
 - Removed CLI

1.0.10 (2014-01-26)
------------------

 - Vendorise docker-py to fix installation problems.

1.0.9 (2013-12-20)
------------------

 - Bugfix: Populate username when getting API key from environment variable

1.0.8 (2013-12-20)
------------------

 - Use ORCHARD_API_KEY environment variable to authenticate, if present

1.0.7 (2013-12-02)
------------------

 - Support multiple port assignments

1.0.6 (2013-12-02)
------------------

 - Make app name optional
 - Improve speed of commands by removing an HTTP request

1.0.5 (2013-11-25)
------------------

 - Output stdout and stderr to correct streams when attaching
 - Many fixes to make `docker attach` faster and more reliable
 - Add `--privileged`` flag to `docker run`

1.0.4 (2013-11-06)
------------------

 - `docker attach` no longer crashes when stdin is not a TTY
 - `docker attach` no longer hangs when stdin is closed

1.0.3 (2013-10-30)
------------------

 - Volumes specified in a Dockerfile will now be created as volumes
   on Orchard. Previously, you had to specify them with a `-v` option
   to `docker run`.

1.0.2 (2013-10-28)
------------------

 - Indent output from `docker inspect`
 - Fix `docker run` outputting `Connection closed by server`
 - Add `-e` and `-p` options to `docker replace`
 - Add `logs()` method to Docker client

1.0.1 (2013-10-04)
------------------

 - Start container after attaching to it so as not to lose output
 - Add `--version` option to client

1.0.0 (2013-10-01)
------------------

 - Initial release
