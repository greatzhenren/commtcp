from datetime import datetime
import threading

_lock = threading.Lock()
_session_coll = {}


def get_session(session_id):
    """
    通过Session的唯一标识获取Session
    :param session_id: Session的唯一标识
    :return: Session，如果没有找到，返回None
    """
    if session_id in _session_coll:
        return _session_coll[session_id]
    return None


def set_session(session_id, session):
    """
    往队列中添加Session，或者改变重变Session
    :param session_id: session的唯一标识
    :param session: Session实体
    """
    _lock.acquire()
    _session_coll[session_id] = session
    _lock.release()


def del_all_expire():
    """
    删除过期Session
    """
    now = datetime.now()
    _lock.acquire()
    for id in list(_session_coll):
        session = _session_coll[id]
        if (now - session._active_time).total_seconds() > session._expired_seconds:
            _session_coll.pop(id)
    _lock.release()


class Session:
    @property
    def session_id(self):
        return self._session_id

    @property
    def addr(self):
        return self._addr

    @property
    def username(self):
        return self._username

    @property
    def active_time(self):
        return self._active_time

    @property
    def data(self):
        return self._data

    def active(self):
        self._active_time = datetime.now()

    def __init__(self, addr, session_id, username, expired_seconds):
        self._session_id = session_id
        self._addr = addr
        self._username = username
        self._active_time = datetime.now()
        self._data = {}
        self._expired_seconds = expired_seconds
