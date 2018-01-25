# -*- coding: utf-8 -*-
"""
    spider.tender_zhejiang.py
    ~~~~~~~~~~~~~~
    :copyright:...
"""
import datetime
import logging
import re
import urllib.error
import urllib.parse
import urllib.request
from copy import deepcopy

from .spider import Spider
from bs4 import BeautifulSoup


class TenderZJU(object):
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
            "districtName": "杭州市",
            "src": '浙江大学',
            "url": None,
            "isNotice": False
        }

    def __del__(self):
        pass

    def get_tenders(self, keys=["存款", "存放"]):
        tenders = []
        for key in keys:
            tenders.extend(self._get_tenders_by_key(key))
        return tenders

    def _get_tenders_by_key(self, key):
        url = "http://zupc.zju.edu.cn/cn20/plus/search.php?"
        values = (('typeid', '35'),
                  ('q', key),
                  ('kwtype', '1'),
                  ('client', 'pub-9280232748837488'),
                  ('forid', '1'),
                  ('ie', 'UTF-8'),
                  ('oe', 'UTF-8'),
                  ('safe', 'active'),
                  ('cof',
                   'GALT:#008000;GL:1;DIV:#336699;VLC:663399;AH:center;BGC:FFFFFF;LBGC:336699;ALC:0000FF;LC:0000FF;T:000000;GFNT:0000FF;GIMP:0000FF;FORID:1'),
                  ('hl', 'zh-CN')
                  )
        search_url = url + urllib.parse.urlencode(values)
        content = self.s.get_content(search_url)
        c = content.decode("utf-8")
        soup = BeautifulSoup(c, "html.parser")
        result = soup.find("div", class_="listbox")
        li_tags = result.find_all("li")
        tenders = []
        for li_tag in li_tags:
            model = deepcopy(self.model)
            model["title"] = li_tag.find("a", target="_blank").text
            detail_str = li_tag.find("span", class_="info").text
            model["noticeID"] = re.search(r"项目编号：(Z.*\d) ", detail_str).group(1) + re.search(r"公告类型：(.*)",
                                                                                             detail_str).group(1)
            model["url"] = "http://zupc.zju.edu.cn" + li_tag.find("a", target="_blank").get("href")
            date = re.search(r"发布日期：(.*)", detail_str).group(1)
            model["endDate"] = date
            model["pubDate"] = date
            tenders.append(model)
        return tenders

        # for entry in re.findall(r"<tr>.*</tr>", result.text):
        #     s = BeautifulSoup(entry, "html.parser")
        #     model = deepcopy(self.model)
        #     model["noticeID"] = s.find("a")["href"]
        #     model["title"] = s.find("a")["title"]
        #     model["url"] = "http://www.hzft.gov.cn" + s.find("a")["href"]
        #     date = re.sub("\[|\]", "", s.find_all("td")[-1].string)
        #     model["endDate"] = date
        #     model["pubDate"] = date
        #     tenders.append(model)
