# pylint: disable=unsupported-binary-operation
"""FilterSet definitions for nautobot_bgp_models."""

import django_filters
from django.db.models import Q
from nautobot.apps.filters import (
    BaseFilterSet,
    CreatedUpdatedModelFilterSetMixin,
    CustomFieldModelFilterSetMixin,
    NaturalKeyOrPKMultipleChoiceFilter,
    NautobotFilterSet,
    RoleModelFilterSetMixin,
    SearchFilter,
    StatusModelFilterSetMixin,
)
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
    autonomous_system_range = django_filters.ModelMultipleChoiceFilter(
        queryset=models.AutonomousSystemRange.objects.all(),
        label="ASN Range",
        method="filter_present_in_asn_range",
    )

    class Meta:
        model = models.AutonomousSystem
        fields = ["id", "asn", "status", "tags", "autonomous_system_range"]

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

    device_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Device.objects.all(),
        label="Device (ID)",
    )

    device = django_filters.ModelMultipleChoiceFilter(
        field_name="device__name",
        queryset=Device.objects.all(),
        to_field_name="name",
        label="Device (name)",
    )

    class Meta:
        model = models.BGPRoutingInstance
        fields = ["id", "autonomous_system", "tags"]


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

    device = django_filters.ModelMultipleChoiceFilter(
        field_name="routing_instance__device__name",
        queryset=Device.objects.all(),
        to_field_name="name",
        label="Device (name)",
    )

    device_id = django_filters.ModelMultipleChoiceFilter(
        field_name="routing_instance__device__id",
        queryset=Device.objects.all(),
        to_field_name="id",
        label="Device (ID)",
    )

    class Meta:
        model = models.PeerGroup
        fields = ["id", "name", "enabled"]


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
        fields = ["id", "name", "enabled"]


class PeerEndpointFilterSet(NautobotFilterSet, RoleModelFilterSetMixin):
    """Filtering of PeerEndpoint records."""

    q = SearchFilter(
        filter_predicates={
            "routing_instance__device__name": "iexact",
            "description": "icontains",
        },
    )

    device = django_filters.ModelMultipleChoiceFilter(
        field_name="routing_instance__device__name",
        queryset=Device.objects.all(),
        to_field_name="name",
        label="Device (name)",
    )

    device_id = django_filters.ModelMultipleChoiceFilter(
        field_name="routing_instance__device__id",
        queryset=Device.objects.all(),
        to_field_name="id",
        label="Device (ID)",
    )

    autonomous_system = django_filters.ModelMultipleChoiceFilter(
        field_name="autonomous_system__asn",
        queryset=models.AutonomousSystem.objects.all(),
        to_field_name="asn",
        label="Autonomous System Number",
    )

    peer_group = django_filters.ModelMultipleChoiceFilter(
        queryset=models.PeerGroup.objects.all(),
        label="Peer Group (id)",
    )

    class Meta:
        model = models.PeerEndpoint
        fields = ["id", "enabled"]


class PeeringFilterSet(
    BaseFilterSet,
    CreatedUpdatedModelFilterSetMixin,
    CustomFieldModelFilterSetMixin,
    StatusModelFilterSetMixin,
):
    """Filtering of Peering records."""

    # TODO(mzb): Add in-memory filtering for Provider, ASN, IP Address, ...
    #  this requires to consider inheritance methods.

    q = SearchFilter(
        filter_predicates={
            "endpoints__routing_instance__device__name": "icontains",
        },
    )

    device = django_filters.ModelMultipleChoiceFilter(
        field_name="endpoints__routing_instance__device__name",
        queryset=Device.objects.all(),
        to_field_name="name",
        label="Device (name)",
    )

    device_id = django_filters.ModelMultipleChoiceFilter(
        field_name="endpoints__routing_instance__device__id",
        queryset=Device.objects.all(),
        to_field_name="id",
        label="Device (ID)",
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


class AddressFamilyFilterSet(BaseFilterSet, CreatedUpdatedModelFilterSetMixin, CustomFieldModelFilterSetMixin):
    """Filtering of AddressFamily records."""

    q = SearchFilter(
        filter_predicates={
            "routing_instance__device__name": "iexact",
        },
    )

    afi_safi = django_filters.MultipleChoiceFilter(choices=choices.AFISAFIChoices)

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
            "routing_instance",
            "afi_safi",
            "vrf",
        ]


class PeerGroupAddressFamilyFilterSet(BaseFilterSet, CreatedUpdatedModelFilterSetMixin, CustomFieldModelFilterSetMixin):
    """Filtering of PeerGroupAddressFamily records."""

    q = SearchFilter(
        filter_predicates={
            "afi_safi": "icontains",
            "peer_group__name": "icontains",
            "peer_group__description": "icontains",
        },
    )

    afi_safi = django_filters.MultipleChoiceFilter(choices=choices.AFISAFIChoices)

    peer_group = django_filters.ModelMultipleChoiceFilter(
        label="Peer Group (ID)",
        queryset=models.PeerGroup.objects.all(),
    )

    class Meta:
        model = models.PeerGroupAddressFamily
        fields = [
            "id",
            "afi_safi",
            "peer_group",
        ]


class PeerEndpointAddressFamilyFilterSet(
    BaseFilterSet, CreatedUpdatedModelFilterSetMixin, CustomFieldModelFilterSetMixin
):
    """Filtering of PeerEndpointAddressFamily records."""

    q = SearchFilter(
        filter_predicates={
            "afi_safi": "icontains",
            "peer_endpoint__routing_instance__device__name": "iexact",
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
