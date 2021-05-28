from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession

from modapi.config import config

import logging
log = logging.getLogger(__name__)

Base = declarative_base()
"""Global declarative base for use in SQLAlchemy ORM class
definitions"""

engine = create_async_engine(config.classic_db_uri, echo=config.echo_sql)
"""An async engine for use by the modapi"""


Session = sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
    future=True
)
""" Session maker for use in API

# This is currently not a scoped session.

# https://docs.sqlalchemy.org/en/14/orm/session_basics.html#using-a-sessionmaker"""


def create_tables():
    """Create any missing tables.

    This is a synchronous call"""
    from sqlalchemy import create_engine
    import modapi.tables.arxiv_tables as arxiv_tables
    sync_url = config.classic_db_uri.replace('+aiomysql', '')
    sync_eng = create_engine(sync_url,
                             echo=config.echo_sql)
    arxiv_tables.metadata.create_all(bind=sync_eng)
