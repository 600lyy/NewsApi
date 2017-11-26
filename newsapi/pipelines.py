# -*- coding: utf-8 -*-

import re
from utilities import logger
from models import Subscription, Article, SubscriptionArticle


class NewsApiPipeline(object):

    def process_item(self, item, spider):
        db_write = getattr(spider, 'db_write', None)

        if db_write:
            try:
                article, url_inserted = Article.get_or_create(
                    article_url=item['article_url'])
                if url_inserted:
                    subs_article, relation_created = SubscriptionArticle.get_or_create(
                        subscription=item['subscription_id'], article=article.id)
                    logger.info(
                        'article_url [ID:%s] is now associated with index_url [ID:%s]',
                        subs_article.article,
                        subs_article.subscription)
                else:
                    subs_article, relation_created = SubscriptionArticle.get_or_create(
                        subscription=item['subscription_id'], article=article.id)
                    if not relation_created:
                        logger.info(
                            'relation between article_url [ID:%s] and index_url [ID:%s] has been ignored',
                            subs_article.article,
                            subs_article.subscription)
                    else:
                        logger.info(
                            'article_url [ID:%s] has created a new relationship with index_url [ID:%s]',
                            subs_article.article,
                            subs_article.subscription)
            except (RuntimeError, KeyError, NameError) as e:
                logger.error(
                    '%s happened when handling %s',
                    str(e),
                    item['article_url'])
                raise RuntimeError('Error received from Scrapy Pipelines')
