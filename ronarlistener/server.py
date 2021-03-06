__author__ = 'Pashtet <pashtetbezd@gmail.com>'

import time
import logging
import socketserver
import threading

from ronarlistener.alarm_notification_handler import AlarmNotificationHandler
from ronarlistener.event_store import EventStore

log = logging.getLogger(__name__)
HOST, PORT = '', 32001


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    """
    Own TCPServer class, also extending from ThreadingMixIn to support multi-threading and
    extending the __init__ method so we can set a reference to our Event Controller
    """

    def __init__(self, server_address, RequestHandlerClass, event_store):
        super().__init__(server_address, RequestHandlerClass)
        self.event_store = event_store


def _init_log():
    # create console handler with with formatting and log level

    LOG_PATH="/var/log/ronar_receiver.log"
    _formatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")

    _file_handler = logging.FileHandler(LOG_PATH)
    _file_handler.setFormatter(_formatter)
    _console_handler = logging.StreamHandler()
    _console_handler.setLevel(logging.DEBUG)
    _console_handler.setFormatter(_formatter)
    # add the handlers to the logger
    _root_logger = logging.getLogger()
    _root_logger.addHandler(_file_handler)
    #_root_logger.addHandler(_console_handler)
    _root_logger.setLevel(logging.DEBUG)


def run():
    event_store = EventStore()

    log.info('Starting Server...')

    # Create the server, binding to HOST on PORT
    server = ThreadedTCPServer((HOST, PORT), AlarmNotificationHandler, event_store)

    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_thread = threading.Thread(target=server.serve_forever)
    # Exit the server thread when the main thread terminates
    server_thread.daemon = True
    server_thread.start()
    log.info('Server loop running in thread: %s', server_thread.name)

    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        log.info('Ctrl-c pressed, exiting ...')
        server.shutdown()
        event_store.close()


# -----------------------------------------------------------------
# Main
# -----------------------------------------------------------------
_init_log()


if __name__ == '__main__':
    run()
