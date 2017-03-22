from socketserver import ThreadingMixIn, TCPServer
from threading import Thread
from commtcp import online
import time


class CommTcpServer:
    def __init__(self):
        self._server=None


    def start(self, ip, port, handler):
        self._is_exit = False
        tr = Thread(target=self._del_sessions)
        tr.start()
        addr = (ip, port)
        self._server = MyThreadingTCPServer(addr, handler)
        self._server.serve_forever()
        self._server.handle_timeout()

    def shutdown(self):
        self._is_exit=True
        self._server.shutdown()

    def _del_sessions(self):
        """
        每隔5秒检查一次Session列表，删除过期的Session
        """
        while (not self._is_exit):
            online.del_all_expire()
            time.sleep(5)


class MyThreadingTCPServer(ThreadingMixIn, TCPServer):
    def handle_timeout(self):
        print('tcp timeout')
