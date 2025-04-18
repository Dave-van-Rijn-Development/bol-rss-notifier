import time
from datetime import datetime

from bol_feed.core.settings import get_settings
from bol_feed.core.types import FeedItemType
import feedparser


def parse_feed() -> list[FeedItemType]:
    settings = get_settings()
    result = feedparser.parse(settings.feed_url)
    items: list[FeedItemType] = list()
    for item in result.entries:
        published: time.struct_time = item.published_parsed
        category = 'Unknown'
        if hasattr(item, 'tags') and item.tags:
            category = item.tags[0].get('term')
        items.append(FeedItemType(
            title=item.title,
            link=item.link,
            description=item.summary,
            category=category,
            pub_date=datetime(published.tm_year, published.tm_mon, published.tm_mday, published.tm_hour,
                              published.tm_min, published.tm_sec),
        ))
    return items
