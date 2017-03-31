import json
from socketserver import StreamRequestHandler
from struct import calcsize, unpack, pack
import datetime

import commtcp.crypto
import commtcp.util
from commtcp import command_id
from commtcp.online import get_session, set_session, Session


class BaseTcpHandler(StreamRequestHandler):
    iv = b'6agvtLexcRYZjV6H'
    _aes = None

    def setup(self):
        super().setup()
        self._session = None

    @classmethod
    def set_key(cls, key):
        cls._aes = commtcp.crypto.Aes(key, BaseTcpHandler.iv)

    def handle(self):
        self.timeout = 120
        head_format = '<3sbb10si'
        fhead = self.rfile.read(calcsize(head_format))
        head_flag, ver, command, session_id, content_len = unpack(head_format, fhead)
        session_id = session_id.decode()
        content = b''
        while True:  # 循环接收Socket包
            buffer = self.rfile.read(content_len)
            content += buffer
            if len(content) == content_len: break
        paras = json.loads(content.decode())
        if command == command_id['Login']:
            self._login(paras['u'], paras['p'])
        else:
            if session_id == None or not get_session(session_id):
                self.send_err('{"code":"SESSION"}')
            else:
                self._session = get_session(session_id)
                self._session.active()
                if commtcp.ACT_LOG_RECODE:
                    print('SESSION:{} {} {} {}'.format(datetime.datetime.now(), self._session.username,
                                                       self._session.session_id, self.client_address))
                if command == command_id['Command']:
                    self.command(paras['cmd'], paras['para'])
                elif command == command_id['Admin']:
                    self.admin(paras['cmd'], paras['para'])
                else:
                    self.msg_handle(command, paras)

    def command(self, cmd, paras):
        """
        客户端向服务器发出的命令，由子类实现
        :param cmd:
        :param paras:
        :return:
        """
        pass

    def admin(selfs, cmd, paras):
        """
        客户端以管理员身份向服务器发出的命令，由子类实现
        设计时注意权限控制
        :param cmd: 命令名称
        :param paras: 参数
        :return:
        """
        pass

    def msg_handle(self, command, paras):
        """
        消息处理，由子类实现
        :param command: 消息类型编号
        :param paras: 参数
        """
        pass

    def send_msg(self, msg):
        self.wfile.write(self._msg_bytes(msg))

    def send_err(self, err):
        self.wfile.write(self._msg_bytes(err, suc=0))

    def _login(self, username, passoword):
        if self.check_auth(username, passoword):
            session_id = commtcp.util.make_password(10)
            session = Session(self.client_address, session_id, username, commtcp.SESSION_TIME_OUT)
            set_session(session_id, session)
            self.send_msg(session_id)
        else:
            self.send_err('{"code":"LOGIN_FAIL"}')

    def check_auth(self, username, password):
        """
        判断用户名和密码是否正确，由子类实现
        :param username: 用户名
        :param password: 密码
        :return: 是否合法用户和密码
        """
        return True

    def _msg_bytes(self, msg, suc=1):
        version, success = 1, suc
        msg_str = BaseTcpHandler._aes.encrypt(msg.encode('utf8'))
        msg_len = len(msg_str)
        fmt = '<3sbbi' + str(msg_len) + 's'
        buf = pack(fmt, b'SMD', version, success, msg_len, msg_str)
        return buf
