import datetime
import logging
import sys
import os
import re

from docopt import docopt
from inspect import getdoc

from .. import __version__
from .command import Command
from .apps_command import AppsCommand
from .docker_command import DockerCommand

from .utils import mkdir

from .errors import UserError
from ..api.errors import HTTPError
from .docopt_command import NoSuchCommand

log = logging.getLogger(__name__)

def main():
    try:
        command = TopLevelCommand()
        command.sys_dispatch()
    except KeyboardInterrupt:
        log.error("\nAborting.")
        exit(1)
    except HTTPError as e:
        log.debug("HTTP error", exc_info=sys.exc_info())

        if e.json and e.json.get('detail'):
            log.error("API error: %s", e.json['detail'])
            log.error("See %s for more detail", command.log_file_path)
        else:
            log.error("There was an API error - see %s", command.log_file_path)
        exit(1)
    except UserError, e:
        log.error(e.msg)
        exit(1)
    except NoSuchCommand, e:
        log.error("No such command: %s", e.command)
        log.error("")
        log.error("\n".join(parse_doc_section("commands:", getdoc(e.supercommand))))
        exit(1)


# stolen from docopt master
def parse_doc_section(name, source):
    pattern = re.compile('^([^\n]*' + name + '[^\n]*\n?(?:[ \t].*?(?:\n|$))*)',
                         re.IGNORECASE | re.MULTILINE)
    return [s.strip() for s in pattern.findall(source)]


class TopLevelCommand(Command):
    """Command-line interface to Orchard.

    Usage:
      orchard [options] apps [ARGS...]
      orchard [options] [-a APP] docker [ARGS...]
      orchard -h|--help

    Options:
      -a APP, --app APP    Specify the Orchard app to run against (required for 'docker')
      --verbose            Show more output
      --version            Print version and exit

    """

    apps = AppsCommand()
    docker = DockerCommand()

    def sys_dispatch(self):
        options = docopt(
            getdoc(self),
            sys.argv[1:],
            options_first=True,
            version=__version__
        )

        command = 'apps' if options['apps'] else 'docker'
        handler = getattr(self, command)
        args = options['ARGS']

        self.set_up_logging(command, options)
        handler.dispatch(args, options)

    def set_up_logging(self, command, global_options):
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter())

        if global_options['--verbose']:
            console_handler.setLevel(logging.DEBUG)
        else:
            console_handler.setLevel(logging.INFO)

        self.log_file_path = self.get_log_file_path(command)
        file_handler = logging.FileHandler(self.log_file_path, delay=True)
        file_handler.setLevel(logging.DEBUG)

        root_logger = logging.getLogger()
        root_logger.addHandler(console_handler)
        root_logger.addHandler(file_handler)
        root_logger.setLevel(logging.DEBUG)

        # Disable requests logging
        logging.getLogger("requests").propagate = False

    def get_log_file_path(self, name):
        log_dir = mkdir(os.path.join(self.global_working_dir, 'log'))
        timestamp = datetime.datetime.now().replace(microsecond=0).isoformat()
        return os.path.join(log_dir, "%s-%s.log" % (timestamp, name))


