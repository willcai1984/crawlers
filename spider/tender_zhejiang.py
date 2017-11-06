# -*- coding: utf-8 -*-
"""
    spider.tender_zhejiang.py
    ~~~~~~~~~~~~~~
    :copyright:...
"""
import datetime
import json
import logging
import time
import urllib.error
import urllib.parse
import urllib.request
from copy import deepcopy

from .spider import Spider


class TenderZheJiang(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.s = Spider()
        self.now = datetime.datetime.now()
        self.model = {
            "createTime": self.now,
            "noticeID": None,
            "bidMenu": None,
            "title": None,
            "projectCode": None,
            "endDate": None,
            "pubDate": None,
            "districtName": None,
            "src": '浙江采购',
            "url": None,
            "isNotice": False
        }

    def __del__(self):
        pass

    def get_tenders(self):
        self._init_spider()
        url = "http://manager.zjzfcg.gov.cn/cms/api/cors/getRemoteResults?"
        values = (('pageSize', '15'),
                  ('pageNo', '1'),
                  ('noticeType', '0'),
                  ('url', 'http://notice.zcy.gov.cn/new/noticeSearch'),
                  ('keyword', '存款')
                  )
        search_url = url + urllib.parse.urlencode(values)
        content = self.s.get_content(search_url)
        tender_dict = json.loads(content)
        articles = tender_dict.get("articles")
        tenders = []
        for article in articles:
            model = deepcopy(self.model)
            model["noticeID"] = article.get("noticeId")
            model["bidMenu"] = article.get("mainBidMenuName")
            model["title"] = article.get("noticeTitle")
            model["projectCode"] = article.get("projectCode")
            model["endDate"] = time.strftime("%Y-%m-%d", time.localtime(float(article.get("noticeEndDate")[:10])))
            model["pubDate"] = time.strftime("%Y-%m-%d", time.localtime(float(article.get("noticePubDate")[:10])))
            model["districtName"] = article.get("districtName")
            model["url"] = "http://www.zjzfcg.gov.cn/innerUsed_noticeDetails/index.html?noticeId=%s" % article.get(
                "noticeId")
            tenders.append(model)
        return tenders

    def _init_spider(self):
        self.s.get_content("http://www.zjzfcg.gov.cn/purchaseNotice/index.html?_=1507798104807")
