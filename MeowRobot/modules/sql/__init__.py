#
# Copyright (C) 2021-2022 by TheAloneteam@Github, < https://github.com/TheAloneTeam >.
# This file is part of < https://github.com/TheAloneTeam/MeowRobot > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/TheAloneTeam/MeowRobot/blob/master/LICENSE >
#
# All rights reserved.

import asyncio
from typing import Any
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from MeowRobot import DB_URI
from MeowRobot import LOGGER as log

if DB_URI and DB_URI.startswith("postgres://"):
    DB_URI = DB_URI.replace("postgres://", "postgresql://", 1)


def start() -> tuple[scoped_session, Any]:
    if DB_URI.startswith("sqlite"):
        engine = create_engine(DB_URI)
    else:
        engine = create_engine(DB_URI, client_encoding="utf8")
    log.info("[PostgreSQL] Connecting to database......")
    BASE.metadata.bind = engine
    BASE.metadata.create_all(engine)
    return scoped_session(sessionmaker(bind=engine, autoflush=False)), engine


BASE = declarative_base()
try:
    SESSION, engine = start()
except Exception as e:
    log.exception(f"[PostgreSQL] Failed to connect due to {e}")
    exit()

log.info("[PostgreSQL] Connection successful, session started.")
