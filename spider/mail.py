# -*- coding: utf-8 -*-
"""
    spider.mail.py
    ~~~~~~~~~~~~~~
    :copyright:...
"""

import smtplib
import logging
from email.mime.text import MIMEText

# 第三方 SMTP 服务
mail_host = "smtp.163.com"  # 设置服务器
mail_user = "willcai1984@163.com"  # 用户名
mail_pass = "cw8205555"  # 口令
sender = 'willcai1984@163.com'

mail_msg_header = '''
<h4>@All:</h4>
<p>勤勤恳恳的小蜘蛛提醒您，有新增招投标记录&nbsp;</p>
<h4 style="color: #2e6c80;">新增招投标记录:</h4>
<table align="center" cellpadding="3" cellspacing="0" style="padding: 1px 1px; border: 1px #ccc solid;">
    <tbody>
        <tr style="height: 28px;" bgcolor="#ACDDEC">
            <th width="30" align="center">ID</th>
            <th width="90" nowrap="nowrap" align="center">地点</th>
            <th width="90" nowrap="nowrap" align="center">来源</th>
            <th align="center">标题</th>
            <th width="120" align="center">发布时间</th>
            <th width="60" align="center">查看</th>
        </tr>'''

mail_msg_footer = '''</tbody></table>'''

mail_msg_entry = '''
        <tr style="height: 28px;background-color:%s;">
            <td align="center">%s</td>
            <td nowrap="nowrap" align="center">%s</td>
            <td nowrap="nowrap" align="center">%s</td>
            <td align="left">%s</td>
            <td align="center">%s</td>
            <td align="center"><a href="%s">查看</a></td>
        </tr>
'''


class Email(object):
    def __init__(self):
        self.s = smtplib.SMTP()
        self.s.connect(mail_host, 25)
        self.s.login(mail_user, mail_pass)
        self.msg = ""
        self.mail_msg_entry_list = []
        self.logger = logging.getLogger(__name__)
        self.id = 1

    def __del__(self):
        self.s.close()

    def process_entry(self, dist, src, title, public, link):
        if self.id % 2:
            # 奇数行
            entry_msg = mail_msg_entry % ("#ffffff", self.id, dist, src, title, public, link)
        else:
            # 偶数行
            entry_msg = mail_msg_entry % ("#eeeeee", self.id, dist, src, title, public, link)
        self.mail_msg_entry_list.append(entry_msg)
        self.id += 1

    def send_txt(self, receivers, subject):
        self.msg = mail_msg_header + "".join(self.mail_msg_entry_list) + mail_msg_footer
        message = MIMEText(self.msg, 'html', 'utf-8')
        message['From'] = sender
        message['To'] = ",".join(receivers)
        message['Subject'] = subject
        try:
            self.s.sendmail(sender, receivers, message.as_string())
            self.logger.info("Send mail successfully")
            return True
        except Exception as e:
            self.logger.error("Send mail failed", exc_info=True)
            return False
