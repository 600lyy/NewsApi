from diffbot_lib import client
from settings import SETTINGS
from utilities import logger
from models import Article
from models import fn
from datetime import datetime
import pprint


class DiffbotCaller(object):
    def __init__(self, **kargs):
        super(DiffbotCaller, self).__init__()
        self.__dict__.update(kargs)
        self.diffbot = client.DiffbotClient()
        self.token = SETTINGS['DIFFBOT_API_TOKEN']
        self.urls = None

    def diffbot_analyze_api(self, query_limit=0):
        resp = []
        exceptions = []
        if query_limit <= 0:
            self.urls = (Article
                         .select()
                         .where(Article.status == 0))
        else:
            self.urls = (Article
                         .select()
                         .where((Article.status == 0) | (Article.status == 1))
                         .order_by(fn.Random())
                         .limit(query_limit))

        for url in self.urls:
            try:
                # print(url.article_url)
                response = self.diffbot.request(
                    url.article_url, self.token, 'analyze')
                pp = pprint.PrettyPrinter(indent=4)
                # print(pp.pprint(response))
                if response['type'] == "article":
                    title = response['objects'][0]['title']
                    if response['objects'][0]['text'] == "":
                        u = Article.update(
                            title=title,
                            modified_utc=datetime.utcnow(),
                        ).where(Article.id == url.id)
                    else:
                        resp.append(response['objects'][0])
                        u = Article.update(
                            status=1,
                            title=title,
                            content=response['objects'][0],
                            modified_utc=datetime.utcnow(),
                        ).where(Article.id == url.id)
                elif response['type'] == "image":
                    u = Article.update(
                        status=3,
                        modified_utc=datetime.utcnow(),
                    ).where(Article.id == url.id)
                elif response['type'] == "video":
                    title = response['title']
                    u = Article.update(
                        status=4,
                        title=title,
                        modified_utc=datetime.utcnow(),
                    ).where(Article.id == url.id)
                else:
                    title = response['title']
                    u = Article.update(
                        status=5,
                        title=title,
                        modified_utc=datetime.utcnow(),
                    ).where(Article.id == url.id)
                u.execute()
            except Exception as e:
                logger.error('%s happened when handling %s', str(e), url)
                exceptions.append(e)
                continue
        return resp
        if exceptions:
            raise RuntimeError('Error received from Diffbot')

    def diffbot_article_api(self, query_limit=0):
        resp = []
        exceptions = []
        if query_limit <= 0:
            self.urls = (Article
                         .select()
                         .where(Article.status == 0))
        else:
            self.urls = (Article
                         .select()
                         .where((Article.status == 0) | (Article.status == 1))
                         .order_by(fn.Random())
                         .limit(query_limit))

        for url in self.urls:
            try:
                print(url.article_url)
                response = self.diffbot.request(
                    url.article_url, self.token, 'article')
                pp = pprint.PrettyPrinter(indent=4)
                # print(pp.pprint(response))

                title = response['objects'][0]['title']
                if response['objects'][0]['text'] == "":
                    u = Article.update(
                        title=title,
                        modified_utc=datetime.utcnow(),
                    ).where(Article.id == url.id)
                else:
                    resp.append(response['objects'][0])
                    u = Article.update(
                        status=1,
                        title=title,
                        content=response['objects'][0],
                        modified_utc=datetime.utcnow(),
                    ).where(Article.id == url.id)
                u.execute()

            except Exception as e:
                logger.error('%s happened when handling %s', str(e), url)
                exceptions.append(e)
                continue
        return resp
        if exceptions:
            raise RuntimeError('Error received from Diffbot')

    def __str__(self):
        return 'DiffbotCaller'

    __repr__ = __str__


if __name__ == '__main__':
    analysis = DiffbotCaller()
    analysis.diffbot_analyze_api(1)
    # analysis.diffbot_article_api(5)
