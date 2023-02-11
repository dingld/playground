from sqlalchemy import Column, String, Integer, DateTime, TEXT, SmallInteger

from scraperx.model.base import DeclarativeBase


class TaskModel(DeclarativeBase):
    __tablename__ = 'task'
    __table_args__ = (
        {
            'mysql_charset': 'utf8',
            'mysql_engine': 'InnoDB',
            'mysql_row_format': 'DYNAMIC',
        },
    )
    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False, unique=True)
    start_urls = Column(TEXT, nullable=False)
    cron = Column(String(40), nullable=False)
    status = Column(SmallInteger, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

    def __repr__(self):
        return '<task:%s (%s)>' % (self.name, self.cron)
