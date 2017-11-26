# -*- coding: utf-8 -*-

import scrapy

class NewsApiItem(scrapy.Item):
    index_url = scrapy.Field()
    subscription_id = scrapy.Field()
    article_url = scrapy.Field()
