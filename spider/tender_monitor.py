# -*- coding: utf-8 -*-
"""
    spider.tender_monitor.py
    ~~~~~~~~~~~~~~
    :copyright:...
"""
import datetime
import logging
from .mongo import Mongo
from .tender_zhejiang import TenderZheJiang
from .wechat import Wechat


class TenderMonitor(object):
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        # 初始化数据库
        db_info = self.config.get('db')
        self.m = Mongo(db_info['ip'], db_info['port'], db_info['database'], db_info.get('username', ''),
                       db_info.get('password', ''), db_info.get('replica', ''))

        self.col_t = self.m.get_utc_col(db_info['collections']['tenders'])
        self.col_token = self.m.get_utc_col(db_info['collections']['tokens'])
        self.tz = TenderZheJiang()
        self.w = Wechat()

    def __del__(self):
        pass

    def process_tender_zj(self):
        is_new = False
        notice_ids = [entry["noticeID"] for entry in self.col_t.find({}, {"noticeID": 1})]
        notice_ids = list(set(notice_ids))
        tenders_zj = self.tz.get_tenders()
        # # 反转排序
        # for tender in list(reversed(tenders_zj)):
        # 正序排布，遇到重复ID，跳出
        for tender in tenders_zj:
            # 如有重复ID，继续
            if tender.get("noticeID") in notice_ids:
                self.logger.info("ID %s is in DB list already" % tender.get("noticeID"))
                break
            is_new = True
            self.col_t.insert(tender)
            self.logger.info("ID %s is inserted into DB successfully" % tender.get("noticeID"))
        return is_new

    def _get_valid_token(self):
        self.logger.info("Get token start")
        token_dict = self.col_token.find_one()
        now = self.m.get_utc_date(datetime.datetime.now())
        # 有记录，判断是否失效，无记录，服务器获取token并存入服务器
        if token_dict:
            # self.m.get_utc_date(datetime.datetime.strptime(tds[2].text.strip(), '%Y-%m-%d %H:%M'))
            self.logger.info("Token exist, check expire time")
            expire = token_dict.get("expire")
            # 距离失效时间小于5mins情况下，重新获取token，否则直接取数据库内数据
            if expire - now < datetime.timedelta(minutes=5):
                self.logger.info("Token will be expired soon, start updating, now is %s, expire is %s" % (now, expire))
                expire = now + datetime.timedelta(hours=2)
                t = self.w.get_token()
                self.col_token.update_one({}, {"$set": {"token": t, "expire": expire}})
                self.logger.info("Get and update token successfully")
            else:
                self.logger.info("Token is valid, now is %s, expire is %s" % (now, expire))
                t = token_dict.get("token")
        else:
            self.logger.info("No token exist, get new one")
            expire = self.m.get_utc_date(datetime.datetime.now() + datetime.timedelta(hours=2))
            t = self.w.get_token()
            self.col_token.insert({"token": t, "expire": expire})
            self.logger.info("Get and insert token successfully")
        return t

    def notice(self, open_id):
        t = self._get_valid_token()
        num = self.col_t.find({"isNotice": False}).count()
        txt = 'ZJcaigou has updated %s messages, if you want to see detail info, please <a href="http://www.zjzfcg.gov.cn/purchaseNotice/index.html?_=150231123123123">click here</a>' % (
            num if num <= 99 else '99+')
        result = self.w.send_txt(t, open_id, txt)
        if result:
            self.col_t.update({"isNotice": False}, {"$set": {"isNotice": True}}, False, True)
