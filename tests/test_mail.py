# -*- coding: utf-8 -*-
import urllib
from unittest import TestCase
from spider.mail import Email


class TestMail(TestCase):
    def test_mail(self):
        m = Email()
        m.send_txt(["caiwei@qjdchina.com"],"test")
