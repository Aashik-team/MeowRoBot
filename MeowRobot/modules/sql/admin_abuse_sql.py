from MeowRobot.modules.sql import SESSION, BASE
from sqlalchemy import Column, String
import threading


class AdminAbuse(BASE):
    __tablename__ = "adminabuse"

    chat_id = Column(String(14), primary_key=True)


LOCK = threading.RLock()


def enable(chat_id):
    with LOCK:
        try:
            chat = SESSION.get(AdminAbuse, str(chat_id))
            if not chat:
                SESSION.add(AdminAbuse(chat_id=str(chat_id)))
                SESSION.commit()
        except:
            SESSION.rollback()


def disable(chat_id):
    with LOCK:
        try:
            chat = SESSION.get(AdminAbuse, str(chat_id))
            if chat:
                SESSION.delete(chat)
                SESSION.commit()
        except:
            SESSION.rollback()


def is_on(chat_id):
    return SESSION.get(AdminAbuse, str(chat_id)) is not None
