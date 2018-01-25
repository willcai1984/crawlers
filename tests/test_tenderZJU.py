from unittest import TestCase
from ..spider import tender_zju


class TestTenderHangzhou(TestCase):
    def test_get_tenders(self):
        t = tender_zju.TenderZJU()
        t.get_tenders()
