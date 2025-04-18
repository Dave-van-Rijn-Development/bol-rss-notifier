from pg_orm import SQLModel
from pg_orm.core.column import Column
from pg_orm.core.column_type import String, DateTime


class FeedItem(SQLModel):
    __table_name__ = 'feed_item'
    title = Column(String, primary_key=True)
    link = Column(String, nullable=False)
    description = Column(String, nullable=False)
    pub_date = Column(DateTime, nullable=False)
    category = Column(String, nullable=False)
