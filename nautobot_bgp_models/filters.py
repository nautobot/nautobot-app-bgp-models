# pylint: disable=unsupported-binary-operation
"""FilterSet definitions for nautobot_bgp_models."""

import django_filters
from django.db.models import Q
from nautobot.apps.filters import (
    NaturalKeyOrPKMultipleChoiceFilter,
    NautobotFilterSet,
    RoleModelFilterSetMixin,
    SearchFilter,
    StatusModelFilterSetMixin,
)
from nautobot.circuits.models import Provider
from nautobot.dcim.models import Device
from nautobot.extras.models import Role
from nautobot.ipam.models import VRF

from . import choices, models


class AutonomousSystemFilterSet(NautobotFilterSet, StatusModelFilterSetMixin):
    """Filtering of AutonomousSystem records."""

    q = SearchFilter(
        filter_predicates={
            "asn": "icontains",
            "description": "icontains",
        },
    )

    provider = NaturalKeyOrPKMultipleChoiceFilter(
        queryset=Provider.objects.all(),
        label="Provider (name or ID)",
        to_field_name="name",
    )

    autonomous_system_range = django_filters.ModelMultipleChoiceFilter(
        queryset=models.AutonomousSystemRange.objects.all(),
        label="ASN Range",
        method="filter_present_in_asn_range",
    )

    class Meta:
        model = models.AutonomousSystem
        fields = ["id", "asn", "status", "tags"]

    def filter_present_in_asn_range(self, queryset, name, value):  # pylint: disable=unused-argument
        """Filter Autonomous Systems that are present in any of the given ASN Ranges."""
        if not value:
            return queryset
        q_obj = Q()
        for asn_range in value:
            q_obj |= Q(asn__gte=asn_range.asn_min, asn__lte=asn_range.asn_max)
        return queryset.filter(q_obj)


class AutonomousSystemRangeFilterSet(NautobotFilterSet):
    """Filtering of AutonomousSystemRange records."""

    q = SearchFilter(
        filter_predicates={
            "name": "icontains",
            "asn_max": "icontains",
            "asn_min": "icontains",
            "description": "icontains",
        },
    )

    class Meta:
        model = models.AutonomousSystemRange
        fields = ["id", "name", "asn_min", "asn_max", "tags"]


class BGPRoutingInstanceFilterSet(NautobotFilterSet, StatusModelFilterSetMixin):
    """Filtering of BGPRoutingInstance records."""

    q = SearchFilter(
        filter_predicates={
            "device__name": "icontains",
        },
    )

    autonomous_system = django_filters.ModelMultipleChoiceFilter(
        field_name="autonomous_system__asn",
        queryset=models.AutonomousSystem.objects.all(),
        to_field_name="asn",
        label="Autonomous System Number",
    )

    device = NaturalKeyOrPKMultipleChoiceFilter(
        queryset=Device.objects.all(),
        to_field_name="name",
        label="Device (name or ID)",
    )

    class Meta:
        model = models.BGPRoutingInstance
        fields = ["id", "tags"]


class PeerGroupFilterSet(NautobotFilterSet, RoleModelFilterSetMixin):
    """Filtering of PeerGroup records."""

    q = SearchFilter(
        filter_predicates={
            "name": "icontains",
            "description": "icontains",
        },
    )

    autonomous_system = django_filters.ModelMultipleChoiceFilter(
        field_name="autonomous_system__asn",
        queryset=models.AutonomousSystem.objects.all(),
        to_field_name="asn",
        label="Autonomous System Number",
    )

    routing_instance = django_filters.ModelMultipleChoiceFilter(
        field_name="routing_instance__id",
        queryset=models.BGPRoutingInstance.objects.all(),
        to_field_name="id",
        label="BGP Routing Instance ID",
    )

    device = NaturalKeyOrPKMultipleChoiceFilter(
        field_name="routing_instance__device",
        queryset=Device.objects.all(),
        to_field_name="name",
        label="Device (name or ID)",
    )

    class Meta:
        model = models.PeerGroup
        fields = ["id", "name", "enabled", "tags"]


class PeerGroupTemplateFilterSet(NautobotFilterSet, RoleModelFilterSetMixin):
    """Filtering of PeerGroupTemplate records."""

    q = SearchFilter(
        filter_predicates={
            "name": "icontains",
            "description": "icontains",
        },
    )

    autonomous_system = django_filters.ModelMultipleChoiceFilter(
        field_name="autonomous_system__asn",
        queryset=models.AutonomousSystem.objects.all(),
        to_field_name="asn",
        label="Autonomous System Number",
    )

    class Meta:
        model = models.PeerGroupTemplate
        fields = ["id", "name", "enabled", "tags"]


class PeerEndpointFilterSet(NautobotFilterSet, RoleModelFilterSetMixin):
    """Filtering of PeerEndpoint records."""

    q = SearchFilter(
        filter_predicates={
            "routing_instance__device__name": "icontains",
            "description": "icontains",
        },
    )

    device = NaturalKeyOrPKMultipleChoiceFilter(
        field_name="routing_instance__device",
        queryset=Device.objects.all(),
        to_field_name="name",
        label="Device (name or ID)",
    )

    autonomous_system = django_filters.ModelMultipleChoiceFilter(
        field_name="autonomous_system__asn",
        queryset=models.AutonomousSystem.objects.all(),
        to_field_name="asn",
        label="Autonomous System Number",
    )

    peer_group = NaturalKeyOrPKMultipleChoiceFilter(
        queryset=models.PeerGroup.objects.all(),
        to_field_name="name",
        label="Peer Group (name or ID)",
    )

    class Meta:
        model = models.PeerEndpoint
        fields = ["id", "enabled", "tags"]


class PeeringFilterSet(StatusModelFilterSetMixin, NautobotFilterSet):
    """Filtering of Peering records."""

    # TODO(mzb): Add in-memory filtering for Provider, ASN, IP Address, ...
    #  this requires to consider inheritance methods.

    q = SearchFilter(
        filter_predicates={
            "endpoints__routing_instance__device__name": "icontains",
        },
    )

    device = NaturalKeyOrPKMultipleChoiceFilter(
        field_name="endpoints__routing_instance__device",
        queryset=Device.objects.all(),
        to_field_name="name",
        label="Device (name or ID)",
    )

    device_role = django_filters.ModelMultipleChoiceFilter(
        field_name="endpoints__routing_instance__device__role__name",
        queryset=Role.objects.all(),
        to_field_name="name",
        label="Device Role (name)",
    )

    peer_endpoint_role = django_filters.ModelMultipleChoiceFilter(
        field_name="endpoints__role__name",
        queryset=Role.objects.all(),
        to_field_name="name",
        label="Peer Endpoint Role (name)",
    )

    class Meta:
        model = models.Peering
        fields = ["id"]


class AddressFamilyFilterSet(NautobotFilterSet):
    """Filtering of AddressFamily records."""

    q = SearchFilter(
        filter_predicates={
            "routing_instance__device__name": "icontains",
        },
    )

    afi_safi = django_filters.MultipleChoiceFilter(choices=choices.AFISAFIChoices)

    device = NaturalKeyOrPKMultipleChoiceFilter(
        field_name="routing_instance__device",
        queryset=Device.objects.all(),
        to_field_name="name",
        label="Device (name or ID)",
    )

    routing_instance = django_filters.ModelMultipleChoiceFilter(
        field_name="routing_instance__id",
        queryset=models.BGPRoutingInstance.objects.all(),
        to_field_name="id",
        label="BGP Routing Instance ID",
    )

    vrf = NaturalKeyOrPKMultipleChoiceFilter(
        label="VRF (name or ID)",
        queryset=VRF.objects.all(),
        to_field_name="name",
    )

    class Meta:
        model = models.AddressFamily
        fields = [
            "id",
        ]


class PeerGroupAddressFamilyFilterSet(NautobotFilterSet):
    """Filtering of PeerGroupAddressFamily records."""

    q = SearchFilter(
        filter_predicates={
            "afi_safi": "icontains",
            "peer_group__name": "icontains",
            "peer_group__description": "icontains",
        },
    )

    afi_safi = django_filters.MultipleChoiceFilter(choices=choices.AFISAFIChoices)

    peer_group = NaturalKeyOrPKMultipleChoiceFilter(
        label="Peer Group (name or ID)",
        queryset=models.PeerGroup.objects.all(),
        to_field_name="name",
    )

    class Meta:
        model = models.PeerGroupAddressFamily
        fields = [
            "id",
        ]


class PeerEndpointAddressFamilyFilterSet(NautobotFilterSet):
    """Filtering of PeerEndpointAddressFamily records."""

    q = SearchFilter(
        filter_predicates={
            "afi_safi": "icontains",
            "peer_endpoint__routing_instance__device__name": "icontains",
            "peer_endpoint__description": "icontains",
        },
    )

    afi_safi = django_filters.MultipleChoiceFilter(choices=choices.AFISAFIChoices)

    peer_endpoint = django_filters.ModelMultipleChoiceFilter(
        label="Peer Endpoint (ID)",
        queryset=models.PeerEndpoint.objects.all(),
    )

    class Meta:
        model = models.PeerEndpointAddressFamily
        fields = [
            "id",
            "afi_safi",
            "peer_endpoint",
        ]
