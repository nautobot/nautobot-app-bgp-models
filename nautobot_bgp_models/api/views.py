"""REST API viewsets for nautobot_bgp_models."""

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from nautobot.apps.api import NautobotModelViewSet
from rest_framework.filters import OrderingFilter

from nautobot_bgp_models import filters
from nautobot_bgp_models import models
from nautobot_bgp_models.api.filter_backends import IncludeInheritedFilterBackend
from . import serializers


class BGPRoutingInstanceViewSet(NautobotModelViewSet):
    """REST API viewset for BGPRoutingInstance records."""

    queryset = models.BGPRoutingInstance.objects.all()
    serializer_class = serializers.BGPRoutingInstanceSerializer
    filterset_class = filters.BGPRoutingInstanceFilterSet


class AutonomousSystemViewSet(NautobotModelViewSet):
    """REST API viewset for AutonomousSystem records."""

    queryset = models.AutonomousSystem.objects.all()
    serializer_class = serializers.AutonomousSystemSerializer
    filterset_class = filters.AutonomousSystemFilterSet


class AutonomousSystemRangeViewSet(NautobotModelViewSet):
    """REST API viewset for AutonomousSystemRange records."""

    queryset = models.AutonomousSystemRange.objects.all()
    serializer_class = serializers.AutonomousSystemRangeSerializer
    filterset_class = filters.AutonomousSystemRangeFilterSet


include_inherited = OpenApiParameter(
    name="include_inherited",
    required=False,
    location=OpenApiParameter.QUERY,
    description="Include inherited configuration values",
    type=OpenApiTypes.BOOL,
)


class InheritableFieldsViewSetMixin:
    """Common mixin for ViewSets that support an additional `include_inherited` query parameter."""

    @extend_schema(parameters=[include_inherited])
    def list(self, request):
        """List all objects of this type."""
        return super().list(request)

    @extend_schema(parameters=[include_inherited])
    def retrieve(self, request, pk=None):
        """Retrieve a specific object instance."""
        return super().retrieve(request, pk=pk)


class PeerGroupViewSet(InheritableFieldsViewSetMixin, NautobotModelViewSet):
    """REST API viewset for PeerGroup records."""

    queryset = models.PeerGroup.objects.all()
    serializer_class = serializers.PeerGroupSerializer
    filter_backends = [IncludeInheritedFilterBackend, OrderingFilter]
    filterset_class = filters.PeerGroupFilterSet


class PeerGroupTemplateViewSet(InheritableFieldsViewSetMixin, NautobotModelViewSet):
    """REST API viewset for PeerGroupTemplate records."""

    queryset = models.PeerGroupTemplate.objects.all()
    serializer_class = serializers.PeerGroupTemplateSerializer
    filterset_class = filters.PeerGroupTemplateFilterSet


class PeerEndpointViewSet(InheritableFieldsViewSetMixin, NautobotModelViewSet):
    """REST API viewset for PeerEndpoint records."""

    queryset = models.PeerEndpoint.objects.all()
    serializer_class = serializers.PeerEndpointSerializer
    filter_backends = [IncludeInheritedFilterBackend, OrderingFilter]
    filterset_class = filters.PeerEndpointFilterSet


class PeeringViewSet(NautobotModelViewSet):
    """REST API viewset for Peering records."""

    queryset = models.Peering.objects.all()
    serializer_class = serializers.PeeringSerializer
    filterset_class = filters.PeeringFilterSet


class AddressFamilyViewSet(InheritableFieldsViewSetMixin, NautobotModelViewSet):
    """REST API viewset for AddressFamily records."""

    queryset = models.AddressFamily.objects.all()
    serializer_class = serializers.AddressFamilySerializer
    filterset_class = filters.AddressFamilyFilterSet


class PeerGroupAddressFamilyViewSet(InheritableFieldsViewSetMixin, NautobotModelViewSet):
    """REST API viewset for PeerGroupAddressFamily records."""

    queryset = models.PeerGroupAddressFamily.objects.all()
    serializer_class = serializers.PeerGroupAddressFamilySerializer
    filterset_class = filters.PeerGroupAddressFamilyFilterSet


class PeerEndpointAddressFamilyViewSet(InheritableFieldsViewSetMixin, NautobotModelViewSet):
    """REST API viewset for PeerEndpointAddressFamily records."""

    queryset = models.PeerEndpointAddressFamily.objects.all()
    serializer_class = serializers.PeerEndpointAddressFamilySerializer
    filterset_class = filters.PeerEndpointAddressFamilyFilterSet
