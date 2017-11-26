#!/usr/bin/env python

from scrapy.spiders import Spider
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from newsapi.items import NewApiItem
from models import Subscription, Article
from urllib.parse import urlparse
from datetime import datetime, timedelta
import re


class ArticleUrlSpider(Spider):
    def __init__(self, db_write=True, *args, **kwargs):
        self.db_write = db_write
        super(ArticleUrlSpider, self).__init__(*args, **kwargs)

    # spider name
    name = 'article_url'

    # TO DO

