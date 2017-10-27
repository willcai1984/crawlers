# -*- coding: utf-8 -*-
"""
    spider.wechat.py
    ~~~~~~~~~~~~~~
    :copyright:...
"""
import datetime
import json
import logging

import requests

# 测试号
appid = "wx23d964155e171297"
secret = "80d5b0a1ba016ea4e5d7c436f42b96be"
values = {'grant_type': 'client_credential',
          'appid': appid,
          'secret': secret}


class Wechat(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.now = datetime.datetime.now()

    def get_token(self):
        content = requests.get("https://api.weixin.qq.com/cgi-bin/token", params=values)
        res_dict = json.loads(content.content)
        return res_dict['access_token']

    def send_txt(self, token, open_id, txt):
        url = "https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token=" + token
        para = {
            "touser": open_id,
            "msgtype": "text",
            "text": {
                "content": txt
            }
        }
        # data = json.dumps(para, ensure_ascii=False, indent=2)
        # 需要指定json编码的时候不会对中文转码为unicode，否则群发的消息会显示为unicode码,不能正确显示
        # r = requests.post(url=url, data=json.dumps(data, ensure_ascii=False, indent=2))
        r = requests.post(url=url, data=json.dumps(para))
        result = r.json()
        self.logger.info("Send txt result is:" + json.dumps(result))
        return result['errcode'] == 0
        # group_id = get_first_group_id()
        # pay_send_all = {
        #     "filter": {
        #         "is_to_all": False,
        #         "group_id": group_id
        #     },
        #     "text": {
        #         "content": str
        #     },
        #     "msgtype": "text"
        # }
        # url = "https://api.weixin.qq.com/cgi-bin/message/mass/sendall?access_token=" + get_token()
        # # 需要指定json编码的时候不会对中文转码为unicode，否则群发的消息会显示为unicode码,不能正确显示
        # r = requests.post(url=url, data=json.dumps(pay_send_all, ensure_ascii=False, indent=2))  # 此处的必须指定此参数
        # result = r.json()
        # # 根据返回码的内容是否为０判断是否成功
        # return result['errcode'] == 0
