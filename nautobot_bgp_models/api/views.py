"""REST API viewsets for nautobot_bgp_models."""

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from nautobot.extras.api.views import CustomFieldModelViewSet, StatusViewSetMixin
from nautobot.core.api.utils import dynamic_import

from nautobot_bgp_models import filters
from nautobot_bgp_models import models
from nautobot_bgp_models.api.filter_backends import IncludeInheritedFilterBackend
from . import serializers


class PluginModelViewSet(CustomFieldModelViewSet):
    """Base class for all REST API viewsets in this plugin."""

    def get_serializer_class(self):
        """Override the default ModelViewSet implementation as it doesn't handle plugins correctly."""
        app_label, model_name = self.queryset.model._meta.label.split(".")
        if self.brief:
            try:
                return dynamic_import(f"{app_label}.api.serializers.Nested{model_name}Serializer")
            except AttributeError:
                pass

        return self.serializer_class


class BGPRoutingInstanceViewSet(PluginModelViewSet, StatusViewSetMixin):
    """REST API viewset for BGPRoutingInstance records."""

    queryset = models.BGPRoutingInstance.objects.all()
    serializer_class = serializers.BGPRoutingInstanceSerializer
    filterset_class = filters.BGPRoutingInstanceFilterSet


class AutonomousSystemViewSet(PluginModelViewSet, StatusViewSetMixin):
    """REST API viewset for AutonomousSystem records."""

    queryset = models.AutonomousSystem.objects.all()
    serializer_class = serializers.AutonomousSystemSerializer
    filterset_class = filters.AutonomousSystemFilterSet


class PeeringRoleViewSet(PluginModelViewSet):
    """REST API viewset for PeeringRole records."""

    queryset = models.PeeringRole.objects.all()
    serializer_class = serializers.PeeringRoleSerializer
    filterset_class = filters.PeeringRoleFilterSet


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


class PeerGroupViewSet(InheritableFieldsViewSetMixin, PluginModelViewSet):
    """REST API viewset for PeerGroup records."""

    queryset = models.PeerGroup.objects.all()
    serializer_class = serializers.PeerGroupSerializer
    filter_backends = [IncludeInheritedFilterBackend]
    filterset_class = filters.PeerGroupFilterSet


class PeerGroupTemplateViewSet(InheritableFieldsViewSetMixin, PluginModelViewSet):
    """REST API viewset for PeerGroupTemplate records."""

    queryset = models.PeerGroupTemplate.objects.all()
    serializer_class = serializers.PeerGroupTemplateSerializer
    filterset_class = filters.PeerGroupTemplateFilterSet


class PeerEndpointViewSet(InheritableFieldsViewSetMixin, PluginModelViewSet):
    """REST API viewset for PeerEndpoint records."""

    queryset = models.PeerEndpoint.objects.all()
    serializer_class = serializers.PeerEndpointSerializer
    filter_backends = [IncludeInheritedFilterBackend]
    filterset_class = filters.PeerEndpointFilterSet


class PeeringViewSet(PluginModelViewSet, StatusViewSetMixin):
    """REST API viewset for Peering records."""

    queryset = models.Peering.objects.all()
    serializer_class = serializers.PeeringSerializer
    filterset_class = filters.PeeringFilterSet


class AddressFamilyViewSet(InheritableFieldsViewSetMixin, PluginModelViewSet):
    """REST API viewset for AddressFamily records."""

    queryset = models.AddressFamily.objects.all()
    serializer_class = serializers.AddressFamilySerializer
    filterset_class = filters.AddressFamilyFilterSet
