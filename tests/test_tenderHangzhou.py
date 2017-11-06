from unittest import TestCase
from ..spider import tender_hangzhou


class TestTenderHangzhou(TestCase):
    def test_get_tenders(self):
        t = tender_hangzhou.TenderHangzhou()
        t.get_tenders()
