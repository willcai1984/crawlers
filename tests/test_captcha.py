# -*- coding: utf-8 -*-
import urllib
from unittest import TestCase
from spider import captcha


class TestCaptcha(TestCase):
    def test_img2string_cv_urlread(self):
        url = "http://zhixing.court.gov.cn/search/captcha.do?captchaId=b85332feafae4db587ff4bf02c11db86&random=0.44174848214523044"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}
        req = urllib.request.Request(url, headers=headers)
        res = urllib.request.urlopen(req, timeout=10)
        content = res.read()
        c = captcha.Captcha()
        c.img2string_cv_urlread(content)
