import unittest
from unittest.mock import Mock

from src.models import CartItem
from src.pricing import PricingError
from src.checkout import CheckoutService, ChargeResult


class TestCheckoutService(unittest.TestCase):

    def setUp(self):
        self.payments = Mock()
        self.email = Mock()
        self.fraud = Mock()
        self.repo = Mock()
        self.pricing = Mock()

        self.checkout = CheckoutService(
            payments=self.payments,
            email=self.email,
            fraud=self.fraud,
            repo=self.repo,
            pricing=self.pricing
        )

        self.items = [CartItem("A", 1000, 1)]

    def test_invalid_user(self):

        result = self.checkout.checkout(
            user_id="   ",
            items=self.items,
            payment_token="tok",
            country="CL"
        )

        self.assertEqual(result, "INVALID_USER")

    def test_pricing_error(self):

        self.pricing.total_cents.side_effect = PricingError("bad cart")

        result = self.checkout.checkout(
            user_id="user1",
            items=self.items,
            payment_token="tok",
            country="CL"
        )

        self.assertTrue(result.startswith("INVALID_CART"))

    def test_rejected_fraud(self):

        self.pricing.total_cents.return_value = 1000
        self.fraud.score.return_value = 90

        result = self.checkout.checkout(
            user_id="user1",
            items=self.items,
            payment_token="tok",
            country="CL"
        )

        self.assertEqual(result, "REJECTED_FRAUD")

    def test_payment_failed(self):

        self.pricing.total_cents.return_value = 1000
        self.fraud.score.return_value = 10
        self.payments.charge.return_value = ChargeResult(ok=False, reason="DECLINED")

        result = self.checkout.checkout(
            user_id="user1",
            items=self.items,
            payment_token="tok",
            country="CL"
        )

        self.assertTrue(result.startswith("PAYMENT_FAILED"))

    def test_successful_checkout(self):

        self.pricing.total_cents.return_value = 1000
        self.fraud.score.return_value = 10
        self.payments.charge.return_value = ChargeResult(ok=True, charge_id="ch1")

        result = self.checkout.checkout(
            user_id="user1",
            items=self.items,
            payment_token="tok",
            country="CL"
        )

        self.assertTrue(result.startswith("OK:"))

        self.repo.save.assert_called_once()
        self.email.send_receipt.assert_called_once()