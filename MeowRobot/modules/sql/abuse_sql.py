from MeowRobot.modules.sql import SESSION, BASE
from sqlalchemy import Column, String
import threading


class Abuse(BASE):
    __tablename__ = "abuse"

    chat_id = Column(String(14), primary_key=True)


LOCK = threading.RLock()


def enable_abuse(chat_id):
    with LOCK:
        try:
            chat = SESSION.get(Abuse, str(chat_id))
            if not chat:
                SESSION.add(Abuse(chat_id=str(chat_id)))
                SESSION.commit()
        except:
            SESSION.rollback()


def disable_abuse(chat_id):
    with LOCK:
        try:
            chat = SESSION.get(Abuse, str(chat_id))
            if chat:
                SESSION.delete(chat)
                SESSION.commit()
        except:
            SESSION.rollback()


def is_abuse(chat_id):
    return SESSION.get(Abuse, str(chat_id)) is not None
