from django.urls import path
from app.api.v1.views import GatesListView, GateDetailView, TransportView, RouteView


urlpatterns = [
    path("gates/", GatesListView.as_view(), name="gates-list"),
    path("gates/<str:gate_id>/", GateDetailView.as_view(), name="gate-detail"),
    path("gates/<str:gate_id>/to/<str:target_gate_id>/", RouteView.as_view(), name="gate-route"),
    path("transport/<str:distance>/", TransportView.as_view(), name="transport"),

]