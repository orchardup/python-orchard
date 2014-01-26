from ..packages.docker import APIError
from datetime import datetime
import sys
import json
import subprocess
from pipes import quote
import re

from .command import Command
from .utils import prettydate
from .socketclient import SocketClient

import logging
log = logging.getLogger(__name__)

class DockerCommand(Command):
    """
    Run commands against the Orchard public Docker cloud.

    Usage: docker [-a APP] COMMAND [ARGS...]

    Options:
        -a APP, --app APP    Specify the Orchard app to run against

    Commands:
        attach           Attach to a running container
        cp               Copy files/folders from the container's filesystem to the host path
        diff             Inspect changes on a container's filesystem
        export           Export the contents of a filesystem as a tar archive
        inspect          Return low-level information on a container/image
        kill             Kill a running container
        logs             Fetch the logs of a container
        ps               List containers
        replace          Replace a running container with a new one, using the specified image
        restart          Restart a running container
        rm               Remove one or more containers
        run              Run a command in a new container
        start            Start a stopped container
        stop             Stop a running container
        top              Lookup the running processes of a container
        version          Print version information

    """

    def dispatch(self, argv, global_options):
        catch_api_error(lambda: super(DockerCommand, self).dispatch(argv, global_options))

    def parse(self, argv, global_options):
        (options, command, handler, command_options) = super(DockerCommand, self).parse(argv, global_options)

        app_name = global_options['--app'] or options['--app']

        if app_name is None:
            app_name = 'default_%s' % self.api.username

        self.docker = self.api.docker(app_name=app_name)

        return (options, command, handler, command_options)

    def attach(self, options):
        """
        Attach to a running container.

        Usage: attach CONTAINER
        """
        container_id = options['CONTAINER']
        container_info = self.docker.inspect_container(container_id)
        with self._attach_to_container(
            container_id,
            interactive=container_info["Config"]["AttachStdin"],
            raw=container_info["Config"]["Tty"]
        ) as c:
            c.run()

    def cp(self, options):
        """
        Copy files/folders from the container's filesystem to the host path

        Usage: cp CONTAINER:RESOURCE HOSTPATH
        """
        (container, resource) = options['CONTAINER:RESOURCE'].split(':')
        response = self.docker.copy(container, resource)
        tar = subprocess.Popen(['tar', '-x', '-C', options['HOSTPATH'], '-f', '-'], stdin=subprocess.PIPE)
        stream(response, tar.stdin, lambda amount: "%s copied" % amount)

    def diff(self, options):
        """
        Inspect changes on a container's filesystem

        Usage: diff CONTAINER
        """
        changes = self.docker.diff(options['CONTAINER'])

        for c in changes:
            print "%s %s" % ("CAD"[c["Kind"]], c["Path"])

    def export(self, options):
        """
        Export the contents of a filesystem as a tar archive

        Usage: export CONTAINER
        """
        response = self.docker.export(options['CONTAINER'])
        stream(response, sys.stdout, lambda amount: "%s exported" % amount)

    def inspect(self, options):
        """
        Return low-level information on a container/image

        Usage: inspect CONTAINER_OR_IMAGE [CONTAINER_OR_IMAGE...]
        """
        array = []

        for identifier in options['CONTAINER_OR_IMAGE']:
            info = catch_404(lambda: self.docker.inspect_container(identifier))
            info = info or catch_404(lambda: self.docker.inspect_image(identifier))

            if info:
                array.append(info)
            else:
                sys.stderr.write("No such container or image: %s\n" % identifier)
                exit(1)

        print json.dumps(array, indent=4)

    def kill(self, options):
        """
        Kill a running container

        Usage: kill CONTAINER [CONTAINER...]
        """
        for container_id in options['CONTAINER']:
            catch_api_error(
                lambda: self.docker.kill(container_id),
                "Killed %s" % container_id
            )

    def logs(self, options):
        """
        Fetch the logs of a container.

        Usage: logs CONTAINER
        """
        container_id = options['CONTAINER']
        with self._attach_to_container(container_id, interactive=False, logs=True, stream=False) as c:
            c.run()

    def ps(self, options):
        """
        List containers.

        Usage: ps [options]

        Options:
            -q    Only display IDs
        """
        containers = self.docker.containers()

        if options['-q']:
            for container in containers:
                print container['Id'][:10]
        else:
            headers = ["ID", "Image", "Command", "Created", "Status", "IP Address", "Ports"]

            for c in containers:
                if c['Ports']:
                    mapping = c['Ports'][0]
                    c['Ports'] = '%s->%s' % (mapping['PublicPort'], mapping['PrivatePort'])
                else:
                    c['Ports'] = ''

            rows = [[
                c['Id'][0:10],
                c['Image'],
                c['Command'][0:20],
                prettydate(datetime.utcfromtimestamp(c['Created'])),
                c['Status'],
                c.get('ExternalIPAddress', ''),
                c['Ports']
            ] for c in containers]

            print self.formatter.table(headers, rows)

    def replace(self, options):
        """
        Replace a running container with a new one, using the specified image

        Usage: replace [options] [-e VAR=VAL...] [-p HOST:CONTAINER...] CONTAINER IMAGE [COMMAND] [ARG...]

        Options:
            -e VAR=VAL  Set an environment variable (can be used multiple times)
            -p PORT     Expose a container's port to the host
        """
        log.info("Pulling image %s", options['IMAGE'])

        new_container = self.docker.replace_container(
            options['CONTAINER'],
            options['IMAGE'],
            ([options['COMMAND']] + options['ARG']) if options['COMMAND'] else [],
            environment=options['-e'],
            ports=self._get_ports(options),
        )
        new_container = self.docker.inspect_container(new_container['Id'])

        binds = {}
        if new_container['Config'].get('Volumes'):
            for (path, _) in new_container['Config']['Volumes'].items():
                binds[""] = path

        self.docker.start(new_container['ID'], binds=binds)

        print new_container['ID'][0:10]

    def restart(self, options):
        """
        Restart a running container

        Usage: restart [options] CONTAINER [CONTAINER...]

        Options:
            -t    Number of seconds to try to stop for before killing the container.
                  Once killed it will then be restarted.
                  Default: 10
        """
        timeout = options['-t'] or 10

        for container_id in options['CONTAINER']:
            catch_api_error(
                lambda: self.docker.restart(container_id, timeout=timeout),
                "Restarted %s" % container_id
            )

    def rm(self, options):
        """
        Remove one or more containers

        Usage: rm [options] CONTAINER [CONTAINER...]

        Options:
            -v    Remove the volumes associated to the container
        """
        for container_id in options['CONTAINER']:
            catch_api_error(
                lambda: self.docker.remove_container(container_id, v=options['-v']),
                "Removed %s" % container_id
            )

    def _get_ports(self, options):
        if options['-p']:
            for port in options['-p']:
                if not re.search('^\d+(:\d+)?$', port):
                    sys.stderr.write("The -p argument must be of the format XXX or XXX:YYY.\n")
                    exit(1)
            return options['-p']


    def run(self, options):
        """
        Run a command in a new container.

        Usage: run [options] [-e VAR=VAL...] [-p HOST:CONTAINER...] IMAGE [COMMAND] [ARG...]

        Options:
            -d          Detached mode: Run container in the background, print new container id
            -e VAR=VAL  Set an environment variable (can be used multiple times)
            -i          Attach this terminal's stdin to the running process
            -m BYTES    Amount of memory, rounded to nearest Orchard container size
                        (in bytes with SI suffix) [default: 512M]
            -p PORT     Expose a container's port to the host. In the format
                        public:private. If the public port is omitted, a random
                        port will be assigned.
            --privileged  Give extended privileges to this container
            -t          Allocate a pseudo-tty
            -v PATH     Mount a volume at the specified path (e.g. /var/lib/mysql)
        """

        ports = self._get_ports(options)

        # Volumes
        volumes = None

        if options['-v']:
            path = options['-v']

            if ':' in path:
                sys.stderr.write("HOST:CONTAINER path format is not currently supported - you can only specify the container path.\n")
                exit(1)

            volumes = {path:{}}

        if options['IMAGE'] != 'ubuntu':
            log.info("Pulling image %s", options['IMAGE'])

        # Memory limit
        mem_limit = None

        if options['-m']:
            match = re.search(r'^(\d+)([kmg])?b?$', options['-m'], re.I)
            if match:
                mem_limit = int(match.group(1))
                unit = match.group(2).lower()
                if unit == 'k':
                    mem_limit *= 1024
                elif unit == 'm':
                    mem_limit *= 1024**2
                elif unit == 'g':
                    mem_limit *= 1024**3
            else:
                sys.stderr.write("Invalid format for -m. It must be bytes, with optional SI unit. E.g.: ")

        container = self.docker.create_container(
            options['IMAGE'],
            ([options['COMMAND']] + options['ARG']) if options['COMMAND'] else [],
            stdin_open=options['-i'],
            tty=options['-t'],
            environment=options['-e'],
            ports=ports,
            privileged=options['--privileged'],
            volumes=volumes,
            mem_limit=mem_limit
        )

        container = self.docker.inspect_container(container['Id'])

        binds = {}
        if container['Config'].get('Volumes'):
            for (path, _) in container['Config']['Volumes'].items():
                binds[""] = path

        if options['-d']:
            self.docker.start(container['ID'], binds=binds)
            print container['ID'][:10]
        else:
            with self._attach_to_container(
                container['ID'],
                interactive=options['-i'],
                logs=True,
                raw=options['-t']
            ) as c:
                self.docker.start(container['ID'], binds=binds)
                c.run()

    def start(self, options):
        """
        Start a stopped container

        Usage: start CONTAINER [CONTAINER...]
        """
        for container_id in options['CONTAINER']:
            catch_api_error(
                lambda: self.docker.start(container_id),
                "Started %s" % container_id
            )

    def stop(self, options):
        """
        Stop a running container.

        Usage: stop [options] CONTAINER [CONTAINER...]

        Options:
            -t    Number of seconds to wait for the container to stop before killing it.
        """
        kwargs = {}

        if options['-t'] is None:
            kwargs['timeout'] = options['-t']

        for container_id in options['CONTAINER']:
            catch_api_error(
                lambda: self.docker.stop(container_id, **kwargs),
                "Stopped %s" % container_id
            )

    def top(self, options):
        """
        Lookup the running processes of a container.

        Usage: top CONTAINER
        """
        top = self.docker.top(options['CONTAINER'])
        print self.formatter.table(top["Titles"], top["Processes"])

    def version(self, options):
        """
        Print version information.

        Usage: version
        """
        client_version = "0.6.4"
        docker_version = self.docker.version()

        print "Client version:", client_version
        print "Server version:", docker_version["Version"]
        print "Git commit:", docker_version["GitCommit"]
        print "Go version:", docker_version["GoVersion"]

    def _attach_to_container(self, container_id, interactive, logs=False, stream=True, raw=False):
        stdio = self.docker.attach_socket(
            container_id,
            params={
                'stdin': 1 if interactive else 0,
                'stdout': 1,
                'stderr': 0,
                'logs': 1 if logs else 0,
                'stream': 1 if stream else 0
            },
            ws=True,
        )

        stderr = self.docker.attach_socket(
            container_id,
            params={
                'stdin': 0,
                'stdout': 0,
                'stderr': 1,
                'logs': 1 if logs else 0,
                'stream': 1 if stream else 0
            },
            ws=True,
        )

        return SocketClient(
            socket_in=stdio,
            socket_out=stdio,
            socket_err=stderr,
            raw=raw,
        )


def catch_api_error(fn, success_message=None):
    try:
        fn()

        if success_message:
            sys.stderr.write("%s\n" % success_message)
    except APIError, e:
        log.debug("Docker API error", exc_info=sys.exc_info())
        sys.stderr.write("%s\n" % (e.explanation or e))


def catch_404(fn):
    try:
        return fn()
    except Exception, e:
        if hasattr(e, 'status') and e.status == 404:
            return None


def stream(from_file, to_file, progress_indicator):
    bytes_written = 0

    while True:
        chunk = from_file.read(4096)

        if chunk:
            to_file.write(chunk)
            bytes_written += len(chunk)
            sys.stderr.write("\r\033[K%s" % progress_indicator(human_readable_size(bytes_written)))
        else:
            sys.stderr.write("\n")
            break


def human_readable_size(num):
    for x in [' bytes','KB','MB','GB','TB']:
        if num < 1024.0:
            return "%3.1f%s" % (num, x)
        num /= 1024.0
