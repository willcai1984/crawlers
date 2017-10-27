# -*- coding: utf-8 -*-
"""
    spider.mail.py
    ~~~~~~~~~~~~~~
    :copyright:...
"""
import datetime
import logging


class Mail(object):
    def __init__(self, col_c, col_m, config):
        self.now = datetime.datetime.now()
        self.col_c = col_c
        self.col_m = col_m
        self.logger = logging.getLogger(__name__)
        self.config = config
        '''
        处理相关数据
        '''
        self.zoro_url = config.get("mail").get("zoroUrl")
        self.shixin_link = "http://shixin.court.gov.cn/"
        self.shixin_name = "失信"
        self.court_link = "http://zhixing.court.gov.cn/search/"
        self.court_name = "执行"
        self.today = datetime.datetime.strptime(str(datetime.date.today()), '%Y-%m-%d')
        self.weekday = datetime.date.today().weekday()
        # self._db_init()

    def __del__(self):
        pass

    def process_mail(self):
        date_model = {
            "date": self.today,
            "isMailDay": False,
            "isMailWeek": False,
            "dayModify": "",
            "weekModify": "",
            "daySend": "",
            "weekSend": ""
        }
        date_dict = self.col_m.find_one({"date": self.today})
        if not date_dict:
            date_dict = date_model.copy()
        isMailDay = date_dict.get("isMailDay")
        isMailWeek = date_dict.get("isMailWeek")

        if self.weekday == self.config.get("mail").get("weekday"):
            self.logger.info("Today is weekend, send weekly report")
            if not isMailWeek:
                mail_name = (self.today - datetime.timedelta(days=6)).strftime('%Y.%m.%d') + "-" + self.today.strftime(
                    '%Y.%m.%d') + "周报" + self.config.get("env")
                mail = Email(mail_name, self.config.get("mail").get("receiversWeekly"))
                result = self._weekly_send(mail)
                self.logger.info("Send weekly report %s successfully" % mail_name)
                if result:
                    date_dict["isMailWeek"] = True
                    date_dict["weekModify"] = self.now
                    date_dict["weekSend"] = mail.msg
                    if self.col_m.find_one({"date": self.today}):
                        self.col_m.update({"date": self.today}, date_dict)
                    else:
                        self.col_m.insert(date_dict)
                    self.logger.info("Update %s weekly db successfully" % mail_name)
            else:
                self.logger.info("This week %s's send flag is true, don't send mail again" % (
                    (self.today - datetime.timedelta(days=6)).strftime('%Y%m%d') + "-" + self.today.strftime('%Y%m%d')))

        self.logger.info("Send daily report")  # 每天判断是否发送daily邮件，每周日判断是否发送weekly邮件
        if not isMailDay:
            mail_name = self.today.strftime('%Y-%m-%d') + "日报" + self.config.get("env")
            mail = Email(mail_name, self.config.get("mail").get("receiversDaily"))
            # 发送daily report
            # 查询所有isdaymail为false的记录，并更新数据库
            result = self._daily_send(mail)
            self.logger.info("Send daily report %s successfully" % mail_name)
            if result:
                date_dict["isMailDay"] = True
                date_dict["dayModify"] = self.now
                date_dict["daySend"] = mail.msg
                if self.col_m.find_one({"date": self.today}):
                    self.col_m.update({"date": self.today}, date_dict)
                else:
                    self.col_m.insert(date_dict)
                self.logger.info("Update %s daily db successfully" % mail_name)
        else:
            self.logger.info("Today %s's send flag is true, don't send mail again" % self.today.strftime('%Y-%m-%d'))

    def _daily_send(self, mail):
        # (id, companyname, createtime, caseid, srclink, src, zorolink,money)
        shixin_entry_list = self.__entry_process("shixin", "Day", "regDate", "gistId", "duty", self.shixin_link,
                                                 self.shixin_name)
        for e in shixin_entry_list:
            mail.process_entry(e)
        court_entry_list = self.__entry_process("court", "Day", "caseCreateTime", "caseCode", "execMoney",
                                                self.court_link, self.court_name)
        for e in court_entry_list:
            mail.process_entry(e)
        return mail.send_daily()

    def _weekly_send(self, mail):
        # (id, companyname, createtime, caseid, srclink, src, zorolink)
        shixin_entry_list = self.__entry_process("shixin", "Week", "regDate", "gistId", "duty", self.shixin_link,
                                                 self.shixin_name)
        for e in shixin_entry_list:
            mail.process_entry(e)
        court_entry_list = self.__entry_process("court", "Week", "caseCreateTime", "caseCode", "execMoney",
                                                self.court_link, self.court_name)
        for e in court_entry_list:
            mail.process_entry(e)
        return mail.send_weekly()

    '''
    col_name: shixin or court
    classify: Day or Week
    creat_name:db内案件发生时间的name
    case_name:db内案件案号的name
    money_name:标的额的name
    link:源网站link
    web_name:源网站名字
    '''

    def __entry_process(self, col_name, classify, create_name, case_name, money_name, link, web_name):
        entry_list = []
        id = 1
        company_dicts = self.col_c.find({col_name + ".count": {"$gt": 0}})
        for company_dict in company_dicts:
            col_punish_list = company_dict.get(col_name).get("punish")
            new_col_punish_list = []
            is_update = False
            for col_punish in col_punish_list:
                if not col_punish.get("is" + classify + "Mail"):
                    is_supplier = company_dict.get("isSupplier", False)
                    is_projecter = company_dict.get("isProjecter", False)
                    company_type = "-"
                    if is_supplier and is_projecter:
                        company_type = "经销商/项目方"
                    elif is_supplier:
                        company_type = "经销商"
                    elif is_projecter:
                        company_type = "项目方"
                    # entry:(id, companyname, type, createtime, caseid, exec_money, srclink, src, zorolink)
                    entry = (id, company_dict.get("name").strip(), company_type, col_punish.get(create_name).strip(),
                             col_punish.get(case_name).strip(), str(col_punish.get(money_name)).strip(), link, web_name,
                             self.zoro_url + str(company_dict.get("_id")))
                    entry_list.append(entry)
                    is_update = True
                    col_punish["is" + classify + "Mail"] = True
                    id += 1
                new_col_punish_list.append(col_punish)
            if is_update:
                self.col_c.update({"name": company_dict.get("name")},
                                  {"$set": {col_name + ".punish": new_col_punish_list,
                                            col_name + ".count": len(new_col_punish_list)}})
        return entry_list


# 第三方 SMTP 服务
mail_host = "smtp.mxhichina.com"  # 设置服务器
mail_user = "spiderman@qjdchina.com"  # 用户名
mail_pass = "Hello123456"  # 口令

sender = 'spiderman@qjdchina.com'

mail_msg_week_header = '''
<h4>@All:</h4>
<p>兢兢业业的小蜘蛛提醒您，本周我司客户中有新增不良记录，请相关人员注意&nbsp;</p>
<h4 style="color: #2e6c80;">本周新增不良记录:</h4>
<table align="center" cellpadding="3" cellspacing="0" style="padding: 1px 1px; border: 1px #ccc solid;">
    <tbody>
        <tr style="height: 28px;" bgcolor="#ACDDEC">
            <th width="30" align="center">ID</th>
            <th nowrap="nowrap" align="center">公司名称</th>
            <th nowrap="nowrap" align="center">类型</th>
            <th width="120" align="center">立案时间</th>
            <th nowrap="nowrap" align="center">案号</th>
            <th width="120" align="center">执行标的</th>
            <th nowrap="nowrap" align="center">来源</th>
            <th width="60" align="center">查看</th>
        </tr>'''

mail_msg_day_header = '''
<h4>@All:</h4>
<p>勤勤恳恳的小蜘蛛提醒您，今天我司客户中有新增不良记录，请相关人员注意&nbsp;</p>
<h4 style="color: #2e6c80;">本日新增不良记录:</h4>
<table align="center" cellpadding="3" cellspacing="0" style="padding: 1px 1px; border: 1px #ccc solid;">
    <tbody>
        <tr style="height: 28px;" bgcolor="#ACDDEC">
            <th width="30" align="center">ID</th>
            <th nowrap="nowrap" align="center">公司名称</th>
            <th nowrap="nowrap" align="center">类型</th>
            <th width="120" align="center">立案时间</th>
            <th nowrap="nowrap" align="center">案号</th>
            <th width="120" align="center">执行标的</th>
            <th nowrap="nowrap" align="center">来源</th>
            <th width="60" align="center">查看</th>
        </tr>'''

mail_msg_footer = '''</tbody></table>'''

mail_msg_entry = '''
        <tr style="height: 28px;">
            <td align="center">%s</td>
            <td nowrap="nowrap" align="left">%s</td>
            <td nowrap="nowrap" align="left">%s</td>
            <td align="center">%s</td>
            <td nowrap="nowrap" align="left">%s</td>
            <td align="left">%s</td>
            <td nowrap="nowrap" align="center"><a href="%s">%s</a></td>
            <td align="center"><a href="%s">查看</a></td>
        </tr>
'''

import smtplib
from email.mime.text import MIMEText


class Email(object):
    def __init__(self, subject, receivers=['caiwei@qjdchina.com']):
        self.smtpObj = smtplib.SMTP()
        self.smtpObj.connect(mail_host, 25)
        # 加密端口 raise SMTPServerDisconnected("Connection unexpectedly closed")
        # self.smtpObj.connect(mail_host, 465)
        self.smtpObj.login(mail_user, mail_pass)
        self.msg = ""
        self.subject = subject
        self.mail_msg_entry_list = []
        self.receivers = receivers
        self.logger = logging.getLogger(__name__)

    def __del__(self):
        self.smtpObj.close()

    '''
    entry:(id,companyname,type,createtime,caseid,exec_money,srclink,src,zorolink)
    '''

    def process_entry(self, entry):
        entry_msg = mail_msg_entry % entry
        self.mail_msg_entry_list.append(entry_msg)

    def send_daily(self):
        if self.mail_msg_entry_list:
            self.msg = mail_msg_day_header + "".join(self.mail_msg_entry_list) + mail_msg_footer
        else:
            self.msg = '''<h4>@All:</h4><p>玉树临风的小蜘蛛很开心的通知您，今天我司客户没有新增的不良数据&nbsp;</p>'''
        return self._send()

    def send_weekly(self):
        if self.mail_msg_entry_list:
            self.msg = mail_msg_week_header + "".join(self.mail_msg_entry_list) + mail_msg_footer
        else:
            self.msg = '''<h4>@All:</h4><p>玉树临风的小蜘蛛很开心的通知您，本周我司客户没有新增的不良数据&nbsp;</p>'''
        return self._send()

    def _send(self):
        message = MIMEText(self.msg, 'html', 'utf-8')
        message['From'] = "{}".format(sender)
        message['To'] = ",".join(self.receivers)
        message['Subject'] = self.subject
        try:
            self.smtpObj.sendmail(sender, self.receivers, message.as_string())
            self.logger.info("Send mail successfully")
            return True
        except Exception as e:
            self.logger.error("Send mail failed", exc_info=True)
            return False
            # self.smtpObj.sendmail(sender, receivers, message.as_string())
