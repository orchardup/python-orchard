# Adapted from https://github.com/benthor/remotty/blob/master/socketclient.py

from select import select
import sys
import tty
import fcntl
import os
import termios
import threading
import time
import errno

import logging
log = logging.getLogger(__name__)


class SocketClient:
    def __init__(self, socket, interactive, keep_running, raw=True):
        self.socket = socket
        self.interactive = interactive
        self.keep_running = keep_running
        self.raw = raw
        self.stdin_fileno = sys.stdin.fileno()
        self.recv_thread = None

    def __enter__(self):
        self.create()
        return self

    def __exit__(self, type, value, trace):
        self.destroy()

    def create(self):
        if os.isatty(sys.stdin.fileno()):
            self.settings = termios.tcgetattr(sys.stdin.fileno())
        else:
            self.settings = None

        if self.interactive:
            self.set_blocking(sys.stdin, False)
            self.set_blocking(sys.stdout, True)

        if self.raw:
            tty.setraw(sys.stdin.fileno())

    def set_blocking(self, file, blocking):
        fd = file.fileno()
        flags = fcntl.fcntl(fd, fcntl.F_GETFL)
        flags = (flags & ~os.O_NONBLOCK) if blocking else (flags | os.O_NONBLOCK)
        fcntl.fcntl(fd, fcntl.F_SETFL, flags)

    def run(self):
        if self.interactive:
            thread = threading.Thread(target=self.send_ws)
            thread.daemon = True
            thread.start()

        self.recv_thread = threading.Thread(target=self.recv_ws)
        self.recv_thread.daemon = True
        self.recv_thread.start()

        self.alive_check()

    def recv_ws(self):
        try:
            while True:
                chunk = self.socket.recv()

                if chunk:
                    sys.stdout.write(chunk)
                    sys.stdout.flush()
                else:
                    break
        except Exception, e:
            log.debug(e)

    def send_ws(self):
        while True:
            r, w, e = select([sys.stdin.fileno()], [], [])

            if r:
                chunk = sys.stdin.read(1)

                if chunk == '':
                    self.socket.send_close()
                    break
                elif self.interactive:
                    try:
                        self.socket.send(chunk)
                    except Exception, e:
                        if hasattr(e, 'errno') and e.errno == errno.EPIPE:
                            break
                        else:
                            raise e
                elif chunk == '\x03':
                    raise KeyboardInterrupt()

    def alive_check(self):
        while True:
            time.sleep(1)

            if not self.recv_thread.is_alive():
                break

            if not self.keep_running():
                break

    def destroy(self):
        if self.settings is not None:
            termios.tcsetattr(self.stdin_fileno, termios.TCSADRAIN, self.settings)

        sys.stdout.flush()

if __name__ == '__main__':
    import websocket

    if len(sys.argv) != 2:
        sys.stderr.write("Usage: python socketclient.py WEBSOCKET_URL\n")
        exit(1)

    url = sys.argv[1]
    socket = websocket.create_connection(url)

    print "connected\r"

    with SocketClient(socket, interactive=True) as client:
        client.run()
