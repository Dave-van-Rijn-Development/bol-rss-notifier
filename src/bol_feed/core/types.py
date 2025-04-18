from datetime import datetime

from pydantic import BaseModel, Field


class FeedItemType(BaseModel):
    model_config = {
        'populate_by_name': True
    }

    title: str
    link: str
    description: str
    pub_date: datetime = Field(alias='pubDate')
    category: str
