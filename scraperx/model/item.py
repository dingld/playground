from sqlalchemy import Column, Integer, DateTime, BLOB

from scraperx.model.base import DeclarativeBase


class ItemModel(DeclarativeBase):
    __tablename__ = 'item'
    __table_args__ = (
        {
            'mysql_charset': 'utf8',
            'mysql_engine': 'InnoDB',
            'mysql_row_format': 'DYNAMIC',
        },
    )
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, nullable=False)
    link_id = Column(Integer, nullable=False)
    items = Column(BLOB, nullable=False)
    created_at = Column(DateTime, nullable=False)

    def __repr__(self):
        return '<task:%s (%s)>' % (self.name, self.cron)
