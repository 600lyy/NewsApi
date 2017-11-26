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

    # retrieve index urls from database and save them into start_urls[]
    start_urls = []
    index_url_dict = {}
    subs = Subscription.select().where(Subscription.active == True)
    for sub in subs:
        start_urls.append(sub.index_url)
        index_url_dict[sub.index_url] = sub.id

    # get a list of top-level domains (.com, .cn, .net ...)
    with open('tlds.txt') as f:
        tlds = f.read().splitlines()
    f.close()

    # extract domain names (*.domain.com.cn) from start_urls
    allowed_domains = []
    for url in start_urls:
        domain = urlparse(url).netloc
        hostname = domain.split(".")
        if len(hostname) > 2:
            if hostname[-2].upper() in tlds:
                hostname = hostname[-3] + "." + \
                    hostname[-2] + "." + hostname[-1]
            else:
                hostname = hostname[-2] + "." + hostname[-1]
        else:
            hostname = ".".join(hostname[0:])
        allowed_domains.append(hostname)
    allowed_domains = list(set(allowed_domains))

    rules = [
        r'//(vip|reg|v|mail|ecard|pay|yuehui)\.',
        r'/videos?/',
        r'/sitemap\.s?html?',
        r'/about\.s?html?',
        r'/register\.',
    ]

    blacklist = []
    unwanted_urls = (Article
                     .select(Article.article_url)
                     .where(
                         (Article.status.in_([3, 4, 5])) &
                         (Article.created_utc >= (datetime.utcnow() - timedelta(hours=2)))))
    for url in unwanted_urls:
        blacklist.append(url.article_url)

    def parse(self, response):
        item = NewApiItem()

        if (".xml" in response.url) or (".rss" in response.url):
            links = Selector(response).xpath('//item/link/text()').extract()

            for link in links:
                item['subscription_id'] = self.index_url_dict[response.url]
                item['article_url'] = link
                yield item
        else:
            extractor = LinkExtractor(
                deny=self.rules,
                allow_domains=self.allowed_domains,
                unique=True)
            links = extractor.extract_links(response)

            for link in links:
                if len(re.sub(r'[\xa0\s]', '', link.text)) <= 4:
                    pass
                elif re.search(r'^https?://.*?/$', link.url) is not None:
                    pass
                elif link.url in self.blacklist:
                    pass
                else:
                    # item['index_url'] = response.url
                    item['subscription_id'] = self.index_url_dict[response.url]
                    item['article_url'] = link.url
                    yield item
