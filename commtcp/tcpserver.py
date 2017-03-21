from socketserver import ThreadingMixIn, TCPServer
from threading import Thread
from commtcp import online
import time


def start(ip, port, handler):
    tr = Thread(target=_del_sessions)
    tr.start()
    addr = (ip, port)
    server = MyThreadingTCPServer(addr, handler)
    server.serve_forever()
    server.handle_timeout()


def _del_sessions():
    while (True):
        online.del_all_expire()
        time.sleep(5)


class MyThreadingTCPServer(ThreadingMixIn, TCPServer):
    def handle_timeout(self):
        print('tcp timeout')
