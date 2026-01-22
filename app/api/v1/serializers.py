from rest_framework import serializers
from app.models import Gate




class GateListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gate
        fields = ["id", "name"]

class ConnectionSerializer(serializers.Serializer):
    id = serializers.CharField()
    hu = serializers.CharField()

class GateDetailSerializer(serializers.ModelSerializer):
    connections = ConnectionSerializer(many=True)
    class Meta:
        model = Gate
        fields = ["id", "name", "connections"]


class TransportQuerySerializer(serializers.Serializer):
    passengers = serializers.IntegerField(min_value=1)
    parking = serializers.IntegerField(min_value=0, required=False, default=0)


class TransportSerializer(serializers.Serializer):
    transport_type = serializers.CharField()
    total_cost_gbp = serializers.FloatField()
    distance_in_au = serializers.FloatField()
    passengers = serializers.IntegerField()
    parking_days = serializers.IntegerField()
    breakdown = serializers.DictField()


class RouteSerializer(serializers.Serializer):
    origin = serializers.CharField()
    destination = serializers.CharField()
    path = serializers.ListField(child=serializers.CharField())
    total_hu = serializers.IntegerField()
    cost_per_passenger_gbp = serializers.FloatField()