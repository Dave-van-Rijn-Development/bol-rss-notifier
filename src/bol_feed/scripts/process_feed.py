from dvrd_smtp.models.smtp_message import SMTPMessage
from dvrd_smtp.models.smtp_server import SMTPServer
from pg_orm.core.session import DatabaseSession

from bol_feed.core.parser import parse_feed
from bol_feed.core.settings import get_settings
from bol_feed.core.types import FeedItemType
from bol_feed.models import FeedItem


def run():
    settings = get_settings()
    DatabaseSession.configure(
        username=settings.database_user,
        password=settings.database_password,
        database_name=settings.database_name,
        host=settings.database_host,
        port=settings.database_port,
    )
    items = parse_feed()
    created_items: list[FeedItem] = []
    updated_items: list[FeedItem] = []
    with DatabaseSession() as session:
        session.create_all()
        for item in items:
            feed_item, updated = _process_item(item=item, session=session)
            if feed_item:
                if updated:
                    updated_items.append(feed_item)
                else:
                    created_items.append(feed_item)
    _notify_items(updated_items=updated_items, created_items=created_items)


def _process_item(*, item: FeedItemType, session: DatabaseSession) -> tuple[FeedItem | None, bool]:
    if existing_item := session.select(FeedItem).where(FeedItem.title == item.title).first():
        if existing_item.pub_date == item.pub_date:
            if existing_item.description != item.description:
                existing_item.description = item.description
                return existing_item, True
        return None, False
    item = FeedItem(
        title=item.title,
        link=item.link,
        description=item.description,
        pub_date=item.pub_date,
        category=item.category,
    )
    session.add(item)
    return item, False


def _notify_items(*, updated_items: list[FeedItem], created_items: list[FeedItem]):
    settings = get_settings()
    updated_items = [f'{item.pub_date.date().isoformat()} {item.title}' for item in updated_items if
                     item.category in settings.notify_categories]
    created_items = [f'{item.pub_date.date().isoformat()} {item.title}' for item in created_items if
                     item.category in settings.notify_categories]
    if not updated_items and not created_items:
        return
    subject = f'Bol RSS feed'
    plain_body = (f'Er zijn {len(created_items)} nieuwe berichten en {len(updated_items)} bijgewerkte berichten '
                  f'gevonden.\n\n'
                  f'Nieuwe berichten:\n'
                  f'{"\n".join(created_items)}\n\n'
                  f'Bijgewerkte berichten:\n'
                  f'{"\n".join(updated_items)}\n\n'
                  f'https://developers.bol.com/en/news/')
    with SMTPServer(host=settings.smtp_host, port=settings.smtp_port, username=settings.smtp_user,
                    password=settings.smtp_password) as server:
        message = SMTPMessage(to_addr=settings.notify_email, from_addr=('Bol Feed', settings.smtp_user),
                              subject=subject, plain_body=plain_body, dkim_cert_path=settings.dkim_path,
                              dkim_selector=settings.dkim_selector)
        server.send_message(message=message)


if __name__ == '__main__':
    run()
