#!/usr/bin/env python3

import threading
import time
import json
import requests
from datetime import datetime

from models import Subscription
from models import Article
from models import SubscriptionArticle
from models import POSTGRES_DB
from utilities import logger
from settings import SETTINGS
from diffbot_caller import DiffbotCaller


def push_aricles(payload):
    if True == SETTINGS['PRODUCTION_FLAG']:
        server_url = "https://newsapi.com/api/v1/ebot/news"
    else:
        server_url = SETTINGS['http_auth'] + "@staging.newsapi.net/api/v1/ebot/news"
    r = requests.post(server_url,
                      headers={'X-Api-Token':SETTINGS['JSON_API_TOKEN'],'Content-Type':
                               'application/json'}, data=payload, timeout=10)
    logger.warning('response code is %d', r.status_code)
    return r.status_code


class ProducerThread(threading.Thread):
    """
    Class ProducerThread
    constructor(time_interval=10)
    """

    def __init__(self, *args, **kwargs):
        super(ProducerThread, self).__init__()
        self.name = 'Producer Thread'
        self.db = kwargs.pop('db', None)
        self.diffbot_caller = kwargs.pop('diffbot_caller', None)
        self.time_interval = kwargs.pop('time_interval', None)
        self.stop_run = False
        if self.db is None:
            self.db = POSTGRES_DB
        if self.diffbot_caller is None:
            self.diffbot_caller = DiffbotCaller()
        if self.time_interval is None:
            self.time_interval = 10

    def push_to_server(self, retry=False):
        try:
            resps = self.diffbot_caller.diffbot_article_api(1)
            if not resps:
                    logger.warning('All text of articles replied from diffbot is empty')
            else:
                try:
                    for res in resps:
                        url = res['pageUrl']
                        title = res['title']
                        # body = (''.join(res['text']))
                        body = res['html']
                        if res['tags']:
                            words = res['tags']
                            key_words = [{'count': w['count'],
                                          'word':w['label']} for w in words]
                        language = res['humanLanguage']
                        if language == 'zh':
                            language = 'cn'
                        # Get all corresponding index_urls of each article_url
                        # return type is selectQuery, which is iterable
                        records = (Subscription
                            .select(Subscription.index_url)
                            .join(SubscriptionArticle)
                            .join(Article)
                            .where(Article.article_url==url))
                        resp_codes = []
                        for rec in records:
                            dl_data = {
                                'entry_page_url': rec.index_url,
                                'news': {
                                    'url': url,
                                    'title':title,
                                    'body': body,
                                    'language': language,
                                    'keywords': key_words,
                                }
                            }

                            # print(dl_data['news']['language'])
                            payload = json.dumps(dl_data,
                                                 ensure_ascii=False).encode('utf-8')
                            resp_codes.append(push_aricles(payload))
                        if 200 in resp_codes:
                            u = Article.update(
                                status=2,
                                modified_utc=datetime.utcnow(),
                            ).where(Article.article_url == url)
                            u.execute()
                #except (KeyError, NameError, AttributeError, TypeError) as e:
                except Exception as e:
                    raise RuntimeError(
                        'Error happened when pushing. Reason: ' + str(e))

        except RuntimeError:
            raise

    def run(self):
        while not self.stop_run:
            try:
                self.push_to_server()
            except RuntimeError as e:
                logger.error(str(e))
            time.sleep(self.time_interval)

    def stop(self):
        self.stop_run = True

    def __str__(self):
        return 'ProducerThread'

    __repr__ = __str__


if __name__ == '__main__':
    producer1 = ProducerThread(time_interval=5)
    producer1.start()
    producer1.join()
