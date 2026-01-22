from django.test import TestCase
from app.models import Gate
from app.services.route_finder import find_cheapest_route


class RouteFinderServiceTest(TestCase):
    def setUp(self):
        Gate.objects.create(
            id="SOL", name="Sol",
            connections=[{"id": "PRX", "hu": "90"}, {"id": "SIR", "hu": "100"}]
        )
        Gate.objects.create(
            id="PRX", name="Proxima",
            connections=[{"id": "SIR", "hu": "10"}]
        )
        Gate.objects.create(
            id="SIR", name="Sirius",
            connections=[]
        )

    def test_direct_route(self):
        result = find_cheapest_route("SOL", "PRX")
        self.assertEqual(result["origin"], "SOL")
        self.assertEqual(result["destination"], "PRX")
        self.assertEqual(result["path"], ["SOL", "PRX"])
        self.assertEqual(result["total_hu"], 90)

    def test_indirect_route(self):
        # SOL -> PRX -> SIR = 90 + 10 = 100
        # SOL -> SIR direct = 100
        result = find_cheapest_route("SOL", "SIR")
        self.assertEqual(result["total_hu"], 100)

    def test_same_origin_destination(self):
        result = find_cheapest_route("SOL", "SOL")
        self.assertEqual(result["total_hu"], 0)
        self.assertEqual(result["path"], ["SOL"])
        self.assertEqual(result["cost_per_passenger_gbp"], 0.0)

    def test_case_insensitive(self):
        result = find_cheapest_route("sol", "prx")
        self.assertEqual(result["origin"], "SOL")
        self.assertEqual(result["destination"], "PRX")

    def test_origin_not_found(self):
        with self.assertRaises(ValueError):
            find_cheapest_route("XYZ", "SOL")

    def test_destination_not_found(self):
        with self.assertRaises(ValueError):
            find_cheapest_route("SOL", "XYZ")

    def test_no_route_exists(self):
        result = find_cheapest_route("SIR", "SOL")
        self.assertIsNone(result)

    def test_cost_calculation(self):
        result = find_cheapest_route("SOL", "PRX")
        # Round trip: 90 HU * 0.10 * 2 = 18.0
        self.assertEqual(result["cost_per_passenger_gbp"], 18.0)
