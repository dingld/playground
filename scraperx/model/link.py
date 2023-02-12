from sqlalchemy import Column, String, Integer, DateTime, SmallInteger

from scraperx.model.base import DeclarativeBase


class LinkModel(DeclarativeBase):
    __tablename__ = 'link'
    __table_args__ = (
        {
            'mysql_charset': 'utf8',
            'mysql_engine': 'InnoDB',
            'mysql_row_format': 'DYNAMIC',
        },
    )
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, nullable=False)
    fingerprint = Column(String(40), nullable=False)
    domain = Column(String(128), nullable=False)
    url = Column(String(4096), nullable=False)
    response_body_size = Column(Integer, nullable=True)
    status_code = Column(String(20), nullable=True)
    retry = Column(SmallInteger, nullable=True)
    error = Column(String(128), nullable=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    fetched_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return '<link:%s (%s)>' % (self.url, self.fingerprint)
