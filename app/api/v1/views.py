from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter

from app.models import Gate
from app.api.v1.serializers import GateListSerializer, GateDetailSerializer, TransportQuerySerializer, TransportSerializer, RouteSerializer
from app.services.transport_cost import cheapest_transport
from app.services.route_finder import find_cheapest_route


class GatesListView(APIView):
    @extend_schema(
        summary="List all gates",
        description="Returns a list of all hyperspace gates in the network",
        responses={200: GateListSerializer(many=True)},
        tags=["Gates"]
    )
    def get(self, request):
        gates = Gate.objects.all().order_by("id")
        serializer = GateListSerializer(gates, many=True)
        return Response(serializer.data)


class GateDetailView(APIView):
    @extend_schema(
        summary="Get gate details",
        description="Returns detailed information about a specific gate including its connections",
        responses={200: GateDetailSerializer, 404: None},
        tags=["Gates"]
    )
    def get(self, request, gate_id: str):
        gate = Gate.objects.filter(id=gate_id.upper()).first()
        if not gate:
            return Response({"detail": "Gate not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = GateDetailSerializer(gate)
        return Response(serializer.data)




class TransportView(APIView):
    @extend_schema(
        summary="Calculate transport cost",
        description="Returns the cheapest vehicle option and cost for traveling to a gate. Distance is in AUs (Astronomical Units).",
        parameters=[
            OpenApiParameter(name="passengers", type=int, required=True, description="Number of passengers (1-5)"),
            OpenApiParameter(name="parking", type=int, required=False, description="Days of parking at the gate (default: 0)")
        ],
        responses={200: TransportSerializer, 400: None},
        tags=["Transport"]
    )
    def get(self, request, distance: float):
        distance = float(distance)
        if distance < 0:
            return Response({"detail": "distance must be >= 0"}, status=status.HTTP_400_BAD_REQUEST)
        
        qs = TransportQuerySerializer(data=request.query_params)
        if not qs.is_valid():
            return Response(qs.errors, status=status.HTTP_400_BAD_REQUEST)

        passengers = qs.validated_data["passengers"]
        parking = qs.validated_data.get("parking", 0)

        try:
            result = cheapest_transport(distance, passengers, parking)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        payload = {
            "distance_in_au": distance,
            "passengers": passengers,
            "parking_days": parking,
            **result,
        }
        serialize_data = TransportSerializer(payload)

        return Response(serialize_data.data, status=status.HTTP_200_OK)


class RouteView(APIView):
    @extend_schema(
        summary="Find cheapest route",
        description="Calculates the cheapest hyperspace route between two gates",
        responses={200: RouteSerializer, 404: None},
        tags=["Gates"]
    )
    def get(self, request, gate_id: str, target_gate_id: str):
        try:
            result = find_cheapest_route(gate_id, target_gate_id)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)

        if result is None:
            return Response(
                {"detail": f"No route found from {gate_id.upper()} to {target_gate_id.upper()}"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = RouteSerializer(result)
        return Response(serializer.data, status=status.HTTP_200_OK)
