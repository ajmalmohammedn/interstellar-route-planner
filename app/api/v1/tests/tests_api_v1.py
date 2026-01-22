from rest_framework.test import APITestCase
from rest_framework import status
from app.models import Gate


class GatesListAPITest(APITestCase):
    def setUp(self):
        Gate.objects.create(id="SOL", name="Sol", connections=[])
        Gate.objects.create(id="PRX", name="Proxima", connections=[])

    def test_list_gates(self):
        response = self.client.get("/api/v1/gates/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_list_gates_ordered_by_id(self):
        response = self.client.get("/api/v1/gates/")
        self.assertEqual(response.data[0]["id"], "PRX")
        self.assertEqual(response.data[1]["id"], "SOL")


class GateDetailAPITest(APITestCase):
    def setUp(self):
        Gate.objects.create(
            id="SOL",
            name="Sol",
            connections=[{"id": "PRX", "hu": "90"}, {"id": "RAN", "hu": "100"}]
        )

    def test_get_gate_detail(self):
        response = self.client.get("/api/v1/gates/SOL/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], "SOL")
        self.assertEqual(response.data["name"], "Sol")
        self.assertEqual(len(response.data["connections"]), 2)

    def test_get_gate_detail_case_insensitive(self):
        response = self.client.get("/api/v1/gates/sol/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], "SOL")

    def test_get_gate_not_found(self):
        response = self.client.get("/api/v1/gates/XYZ/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TransportAPITest(APITestCase):
    def test_transport_personal(self):
        response = self.client.get("/api/v1/transport/100/?passengers=2&parking=0")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["transport_type"], "Personal")
        self.assertEqual(response.data["total_cost_gbp"], 30.0)

    def test_transport_parking_optional(self):
        response = self.client.get("/api/v1/transport/100/?passengers=2")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["parking_days"], 0)

    def test_transport_missing_passengers(self):
        response = self.client.get("/api/v1/transport/100/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_transport_negative_distance(self):
        response = self.client.get("/api/v1/transport/-10/?passengers=2")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_transport_too_many_passengers(self):
        response = self.client.get("/api/v1/transport/100/?passengers=6")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class RouteAPITest(APITestCase):
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
        response = self.client.get("/api/v1/gates/SOL/to/PRX/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["origin"], "SOL")
        self.assertEqual(response.data["destination"], "PRX")
        self.assertEqual(response.data["path"], ["SOL", "PRX"])
        self.assertEqual(response.data["total_hu"], 90)
        # Round trip: 90 * 0.10 * 2 = 18.0
        self.assertEqual(response.data["cost_per_passenger_gbp"], 18.0)

    def test_indirect_route_finds_shortest(self):
        response = self.client.get("/api/v1/gates/SOL/to/SIR/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_hu"], 100)

    def test_same_origin_destination(self):
        response = self.client.get("/api/v1/gates/SOL/to/SOL/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_hu"], 0)
        self.assertEqual(response.data["path"], ["SOL"])

    def test_route_case_insensitive(self):
        response = self.client.get("/api/v1/gates/sol/to/prx/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["origin"], "SOL")

    def test_route_origin_not_found(self):
        response = self.client.get("/api/v1/gates/XYZ/to/SOL/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_route_destination_not_found(self):
        response = self.client.get("/api/v1/gates/SOL/to/XYZ/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_no_route_exists(self):
        # SIR has no outgoing connections
        response = self.client.get("/api/v1/gates/SIR/to/SOL/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
