# -*- coding: utf-8 -*-
"""
    spider.tender_hangzhou.py
    ~~~~~~~~~~~~~~
    :copyright:...
"""
import datetime
import logging
import re
from copy import deepcopy

from bs4 import BeautifulSoup

from .spider import Spider


class TenderHangzhou(object):
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
            "districtName": "杭州",
            "src": '杭州财税',
            "url": None,
            "isNotice": False
        }

    def __del__(self):
        pass

    def get_tenders(self):
        content = self.s.get_content("http://www.hzft.gov.cn/col/col146/index.html")
        c = content.decode("utf-8")
        soup = BeautifulSoup(c, "html.parser")
        result = soup.find("div", id="1079")
        tenders = []
        for entry in re.findall(r"<tr>.*</tr>", result.text):
            s = BeautifulSoup(entry, "html.parser")
            model = deepcopy(self.model)
            model["noticeID"] = s.find("a")["href"]
            model["title"] = s.find("a")["title"]
            model["url"] = "http://www.hzft.gov.cn" + s.find("a")["href"]
            date = re.sub("\[|\]", "", s.find_all("td")[-1].string)
            model["endDate"] = date
            model["pubDate"] = date
            tenders.append(model)
        return tenders
