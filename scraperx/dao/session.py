from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from scraperx.utils.config import read_config_key

SQLALCHEMY_DATABASE_URL_DEFAULT = read_config_key("dao.session.sqlalchemy")

SessionLocal: sessionmaker = sessionmaker(autocommit=False, autoflush=False)


def bind_url(url: str = ""):
    if not url:
        url = SQLALCHEMY_DATABASE_URL_DEFAULT
    engine = create_engine(
        url
    )
    SessionLocal.kw['bind'] = engine


if __name__ == "__main__":
    from scraperx.model.item import *
    from scraperx.model.link import *
    from scraperx.model.task import *
    from scraperx.model.base import DeclarativeBase

    print("sqlalchemy path: %s" % SQLALCHEMY_DATABASE_URL_DEFAULT)
    DeclarativeBase.metadata.create_all(create_engine(SQLALCHEMY_DATABASE_URL_DEFAULT))
