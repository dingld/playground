from sqlalchemy import Column, String, Integer, DateTime, TEXT, SmallInteger

from scraperx.model.base import DeclarativeBase


class HtmlRuleModel(DeclarativeBase):
    __tablename__ = 'html_parser'
    __table_args__ = (
        {
            'mysql_charset': 'utf8',
            'mysql_engine': 'InnoDB',
            'mysql_row_format': 'DYNAMIC',
        },
    )
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    domain = Column(String(128), nullable=False)
    path = Column(String(4096), nullable=False)
    type = Column(SmallInteger, nullable=False)
    status = Column(SmallInteger, nullable=False)
    rules = Column(TEXT, nullable=False)
    ttl = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

    def __repr__(self):
        return '<rule:%s (%s)>' % (self.domain, self.name)
