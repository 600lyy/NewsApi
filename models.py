#!/usr/bin/env python3

import datetime
import os
import sys

# from peewee import BigIntegerField, IntegerField, SQL
from peewee import CharField, TextField, BooleanField
from peewee import SmallIntegerField
from peewee import DateTimeField, TimeField
from peewee import CompositeKey
from peewee import ForeignKeyField
from peewee import Model
from peewee import PrimaryKeyField
from peewee import fn

from settings import SETTINGS
from settings import DB as POSTGRES_DB
from utilities import logger
from xlrd import open_workbook


class DateTimeWithTimeZoneField(DateTimeField):
    '''Time stamp field with time zone support for PostgreSQL'''
    db_field = 'TIMESTAMP WITH TIME ZONE'


class TimeWithTimeZoneField(TimeField):
    db_field = 'TIME WITH TIME ZONE'


class BaseModel(Model):

    class Meta:
        database = SETTINGS['DB']


class Subscription(BaseModel):
    id = PrimaryKeyField()
    index_url = CharField(max_length=200, unique=True)
    active = BooleanField(default=True)
    created_utc = DateTimeField(default=datetime.datetime.utcnow)


class Article(BaseModel):
    """
    status code:
        0. The url has not been sent to diffbot
        1. diffbot failed to retrieve text for the url
        2. Article has been successfully pushed to the server
        3. diffbot analysis api returns an "image" type for the url
        4. diffbot analysis api returns a "video" type for the url
        5. all other types besides article, image and video
    """
    id = PrimaryKeyField()
    article_url = CharField(max_length=200, unique=True)
    status = SmallIntegerField(default=0)
    title = CharField(max_length=100, null=True)
    content = TextField(null=True)
    created_utc = DateTimeField(default=datetime.datetime.utcnow)
    modified_utc = DateTimeField(null=True)


class SubscriptionArticle(BaseModel):
    subscription = ForeignKeyField(
        Subscription, to_field='id', related_name='articles',
        on_delete='CASCADE')
    article = ForeignKeyField(
        Article, to_field='id', related_name='subscriptions',
        on_delete='CASCADE')
    created_utc = DateTimeField(default=datetime.datetime.utcnow)

    class Meta:
        primary_key = CompositeKey('subscription', 'article')


def create_tables(tables, reset=False):
    for table in tables:
        if not table.table_exists():
            table.create_table()
            logger.info('Table %s created' % table.__name__)
        elif reset:
            table.drop_table(cascade=True)
            logger.info('Existing table %s dropped' % table.__name__)
            table.create_table()
            logger.info('Table %s created' % table.__name__)
        else:
            logger.info('Table %s already exists' % table.__name__)
    return


def feed_subscription_url_from_xml(fname):
    if not os.path.exists(fname):
        logger.warn('%s does not exist' % fname)
        return

    counter = 0
    with open_workbook(fname) as wb:
        s = wb.sheet_by_index(0)
        for row in range(1, s.nrows):
            Subscription.get_or_create(
                index_url=s.cell(row, 1).value
            )
            counter += 1
        logger.info('%s index_url(s) has been inserted' % counter)
    return


def feed_article_url_from_xls(fname):
    if not os.path.exists(fname):
        logger.warn('%s does not exist' % fname)
        return

    with open_workbook(fname) as wb:
        s = wb.sheet_by_index(1)
        for row in range(1, s.nrows):
            Article.get_or_create(
                article_url=s.cell(row, 1).value
            )
    return


def feed_subscription_article_from_xls(fname):
    if not os.path.exists(fname):
        logger.warn('%s does not exist' % fname)
        return

    with open_workbook(fname) as wb:
        s = wb.sheet_by_index(2)
        for row in range(1, s.nrows):
            SubscriptionArticle.get_or_create(
                subscription=s.cell(row, 0).value,
                article=s.cell(row, 1).value
            )
    return


if __name__ == '__main__':
    print('Using PRODUCTION database? %s' % SETTINGS['PRODUCTION_FLAG'])
    if len(sys.argv) > 1 and sys.argv[1] == '--nointeraction':
        pass
    else:
        r = input(
            'Deleting and initializing tables, press Enter to continue...\n')
        if r:
            print('Aborted')
            sys.exit(1)
    tables = [Subscription, Article, SubscriptionArticle]
    create_tables(tables, reset=True)

    # abs_path = os.path.abspath(__file__)
    # cur_dir = os.path.dirname(abs_path)
    # test_url = os.path.join(cur_dir, 'test/data/test_url.xlsx')
    # feed_subscription_url_from_xml(test_url)
    # feed_article_url_from_xls(test_url)
    # feed_subscription_article_from_xls(test_url)
    POSTGRES_DB.close()
