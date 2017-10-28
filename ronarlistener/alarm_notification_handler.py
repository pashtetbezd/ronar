"""
Handles receiving of the alarm notification messages on the TCP/IP socket
"""
__author__ = 'Pashtet <pashtetbezd@gmail.com>'

import logging
import socketserver
from datetime import datetime
import time
from enum import Enum
from ronarlistener.message import Message, Protocol

log = logging.getLogger(__name__)
TIME_INTERVAL = 40


class AlarmNotificationHandler(socketserver.BaseRequestHandler):

    def handle(self):

        # self.request is the TCP socket connected to the client
        line = self.request.recv(1024).strip().decode('utf8')

        try:
            message = Message(line);
            self.server.event_store.store_event(message)
            response = message.getResponse()

            if response is None:
                self.request.close()
                return

            log.info("Response: " + response)
            self.request.sendall(response.encode('utf8'))

        except OSError as error:
            log.warn('Got error while reading from socket {}'.format(error.args[0]), exc_info=error)