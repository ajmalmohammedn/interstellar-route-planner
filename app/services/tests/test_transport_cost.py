from django.test import TestCase
from app.services.transport_cost import cheapest_transport


class TransportCostServiceTest(TestCase):
    def test_personal_transport_no_parking(self):
        result = cheapest_transport(100, 2, 0)
        self.assertEqual(result["transport_type"], "Personal")
        self.assertEqual(result["total_cost_gbp"], 30.0)  # 100 * 0.30

    def test_personal_transport_with_parking(self):
        result = cheapest_transport(100, 2, 2)
        self.assertEqual(result["transport_type"], "Personal")
        self.assertEqual(result["total_cost_gbp"], 40.0)  # 100 * 0.30 + 2 * 5

    def test_hstc_cheaper_with_long_parking(self):
        # Personal: 10 * 0.30 + 10 * 5 = 53
        # HSTC: 10 * 0.45 = 4.5
        result = cheapest_transport(10, 2, 10)
        self.assertEqual(result["transport_type"], "HSTC")
        self.assertEqual(result["total_cost_gbp"], 4.5)

    def test_hstc_only_for_5_passengers(self):
        result = cheapest_transport(100, 5, 0)
        self.assertEqual(result["transport_type"], "HSTC")
        self.assertEqual(result["total_cost_gbp"], 45.0)  # 100 * 0.45

    def test_invalid_negative_distance(self):
        with self.assertRaises(ValueError):
            cheapest_transport(-10, 2, 0)

    def test_invalid_zero_passengers(self):
        with self.assertRaises(ValueError):
            cheapest_transport(100, 0, 0)

    def test_invalid_too_many_passengers(self):
        with self.assertRaises(ValueError):
            cheapest_transport(100, 6, 0)

    def test_invalid_negative_parking(self):
        with self.assertRaises(ValueError):
            cheapest_transport(100, 2, -1)
