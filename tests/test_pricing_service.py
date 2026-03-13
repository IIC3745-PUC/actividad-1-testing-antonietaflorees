import unittest

from src.models import CartItem
from src.pricing import PricingService, PricingError


class TestPricingService(unittest.TestCase):

    def setUp(self):
        self.pricing = PricingService()

    # ---------- subtotal ----------

    def test_subtotal_correcto(self):
        items = [
            CartItem("A", 1000, 2),
            CartItem("B", 500, 1)
        ]

        result = self.pricing.subtotal_cents(items)

        self.assertEqual(result, 2500)

    def test_subtotal_qty_invalida(self):
        items = [CartItem("A", 1000, 0)]

        with self.assertRaises(PricingError):
            self.pricing.subtotal_cents(items)

    def test_subtotal_precio_negativo(self):
        items = [CartItem("A", -100, 1)]

        with self.assertRaises(PricingError):
            self.pricing.subtotal_cents(items)

    # ---------- coupons ----------

    def test_coupon_save10(self):

        result = self.pricing.apply_coupon(10000, "SAVE10")

        self.assertEqual(result, 9000)

    def test_coupon_clp2000(self):

        result = self.pricing.apply_coupon(5000, "CLP2000")

        self.assertEqual(result, 3000)

    def test_coupon_invalido(self):

        with self.assertRaises(PricingError):
            self.pricing.apply_coupon(5000, "ABC")

    # ---------- taxes ----------

    def test_tax_cl(self):

        result = self.pricing.tax_cents(10000, "CL")

        self.assertEqual(result, 1900)

    def test_tax_us(self):

        result = self.pricing.tax_cents(10000, "US")

        self.assertEqual(result, 0)

    def test_tax_eu(self):

        result = self.pricing.tax_cents(10000, "EU")

        self.assertEqual(result, 2100)

    # ---------- shipping ----------

    def test_shipping_cl_gratis(self):

        result = self.pricing.shipping_cents(20000, "CL")

        self.assertEqual(result, 0)

    def test_shipping_cl_pagado(self):

        result = self.pricing.shipping_cents(10000, "CL")

        self.assertEqual(result, 2500)

    def test_shipping_us(self):

        result = self.pricing.shipping_cents(10000, "US")

        self.assertEqual(result, 5000)

    # ---------- total ----------

    def test_total(self):

        items = [CartItem("A", 10000, 1)]

        total = self.pricing.total_cents(
            items,
            coupon_code="SAVE10",
            country="CL"
        )

        self.assertTrue(total > 0)