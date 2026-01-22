from django.test import TestCase
from app.models import Gate


class GateModelTest(TestCase):
    def setUp(self):
        Gate.objects.create(
            id="SOL",
            name="Sol",
            connections=[{"id": "PRX", "hu": "90"}, {"id": "RAN", "hu": "100"}]
        )

    def test_gate_str(self):
        gate = Gate.objects.get(id="SOL")
        self.assertEqual(str(gate), "SOL - Sol")

