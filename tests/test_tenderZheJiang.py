from unittest import TestCase
from spider import tender_zhejiang


class TestTenderZheJiang(TestCase):
    def test_get_tender(self):
        t = tender_zhejiang.TenderZheJiang()
        t.get_tenders()
