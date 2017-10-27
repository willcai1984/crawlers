# -*- coding: utf-8 -*-
"""
    spider.mail.py
    ~~~~~~~~~~~~~~
    :copyright:...
"""
import pymongo
import pytz
from bson.codec_options import CodecOptions


class Mongo(object):
    def __init__(self, ip, port, db, user='', passwd='', repl=""):
        if repl:
            self.con = pymongo.MongoClient(ip, int(port), replicaset=repl)
        else:
            self.con = pymongo.MongoClient(ip, int(port))
        self.db = self.con.get_database(db)
        if user and passwd:
            self.db.authenticate(user, passwd, mechanism='SCRAM-SHA-1')
        self.tz = pytz.timezone(pytz.country_timezones('cn')[0])

    def __del__(self):
        self.con.close()

    def get_utc_col(self, col_name):
        return self.db.get_collection(col_name).with_options(
            codec_options=CodecOptions(tz_aware=True, tzinfo=pytz.timezone(pytz.country_timezones('cn')[0])))

    # def replace(self, condition, info):
    #     if condition:
    #         # 判断是否已经有记录（id及姓名），如有，覆盖，如无，插入
    #         if self.col.find(condition):
    #             self.col.update(condition, info)
    #         else:
    #             self.col.insert(info)
    #     else:
    #         self.col.insert(info)

    def get_utc_date(self, date):
        return self.tz.localize(date)
