# pylint: disable=unsupported-binary-operation
"""FilterSet definitions for nautobot_bgp_models."""

import django_filters

from django.db.models import Q

from nautobot.dcim.models import Device
from nautobot.apps.filters import (
    StatusModelFilterSetMixin,
    CreatedUpdatedModelFilterSetMixin,
    CustomFieldModelFilterSetMixin,
)
from nautobot.extras.filters.mixins import RoleModelFilterSetMixin
from nautobot.ipam.models import VRF
from nautobot.apps.filters import BaseFilterSet
from nautobot.extras.models import Role

from . import choices, models


class AutonomousSystemFilterSet(
    BaseFilterSet, CreatedUpdatedModelFilterSetMixin, CustomFieldModelFilterSetMixin, StatusModelFilterSetMixin
):
    """Filtering of AutonomousSystem records."""

    q = django_filters.CharFilter(
        method="search",
        label="Search",
    )

    def search(self, queryset, name, value):  # pylint: disable=unused-argument
        """Free-text search method implementation."""
        if not value.strip():
            return queryset
        return queryset.filter(Q(asn__icontains=value) | Q(description__icontains=value)).distinct()

    class Meta:
        model = models.AutonomousSystem
        fields = ["id", "asn", "status", "tags"]


class AutonomousSystemRangeFilterSet(
    BaseFilterSet,
    CreatedUpdatedModelFilterSetMixin,
    CustomFieldModelFilterSetMixin,
):
    """Filtering of AutonomousSystemRange records."""

    q = django_filters.CharFilter(
        method="search",
        label="Search",
    )

    def search(self, queryset, name, value):  # pylint: disable=unused-argument
        """Free-text search method implementation."""
        if not value.strip():
            return queryset

        return queryset.filter(
            Q(name=value) | Q(asn_max__icontains=value) | Q(asn_min__icontains=value) | Q(description__icontains=value)
        ).distinct()

    class Meta:
        model = models.AutonomousSystemRange
        fields = ["id", "name", "asn_min", "asn_max", "tags"]


class BGPRoutingInstanceFilterSet(
    BaseFilterSet, CreatedUpdatedModelFilterSetMixin, CustomFieldModelFilterSetMixin, StatusModelFilterSetMixin
):
    """Filtering of BGPRoutingInstance records."""

    q = django_filters.CharFilter(
        method="search",
        label="Search",
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

    def search(self, queryset, name, value):  # pylint: disable=unused-argument
        """Free-text search method implementation."""
        if not value.strip():
            return queryset
        return queryset.filter(Q(device__name__icontains=value)).distinct()


class PeerGroupFilterSet(RoleModelFilterSetMixin, BaseFilterSet):
    """Filtering of PeerGroup records."""

    q = django_filters.CharFilter(
        method="search",
        label="Search",
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

    def search(self, queryset, name, value):  # pylint: disable=unused-argument
        """Free-text search method implementation."""
        if not value.strip():
            return queryset
        return queryset.filter(Q(name__icontains=value) | Q(description__icontains=value)).distinct()


class PeerGroupTemplateFilterSet(RoleModelFilterSetMixin, BaseFilterSet):
    """Filtering of PeerGroupTemplate records."""

    q = django_filters.CharFilter(
        method="search",
        label="Search",
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

    def search(self, queryset, name, value):  # pylint: disable=unused-argument
        """Free-text search method implementation."""
        if not value.strip():
            return queryset
        return queryset.filter(Q(name__icontains=value) | Q(description__icontains=value)).distinct()


class PeerGroupTemplateEndpointFilterSet(RoleModelFilterSetMixin, BaseFilterSet):
    """Filtering of PeerGroupTemplateEndpoint records."""

    q = django_filters.CharFilter(
        method="search",
        label="Search",
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

    peer_group_template = django_filters.ModelMultipleChoiceFilter(
        queryset=models.PeerGroupTemplate.objects.all(),
        label="Peer Group Template (id)",
    )

    class Meta:
        model = models.PeerGroupTemplateEndpoint
        fields = ["id", "enabled"]

    def search(self, queryset, name, value):  # pylint: disable=unused-argument
        """Free-text search method implementation."""
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(routing_instance__device__name__iexact=value) | Q(description__icontains=value)
        ).distinct()


class PeerEndpointFilterSet(RoleModelFilterSetMixin, BaseFilterSet):
    """Filtering of PeerEndpoint records."""

    q = django_filters.CharFilter(
        method="search",
        label="Search",
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

    def search(self, queryset, name, value):  # pylint: disable=unused-argument
        """Free-text search method implementation."""
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(routing_instance__device__name__iexact=value) | Q(description__icontains=value)
        ).distinct()


class PeeringFilterSet(
    BaseFilterSet,
    CreatedUpdatedModelFilterSetMixin,
    CustomFieldModelFilterSetMixin,
    StatusModelFilterSetMixin,
):
    """Filtering of Peering records."""

    # TODO(mzb): Add in-memory filtering for Provider, ASN, IP Address, ...
    #  this requires to consider inheritance methods.

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

    afi_safi = django_filters.MultipleChoiceFilter(choices=choices.AFISAFIChoices)

    routing_instance = django_filters.ModelMultipleChoiceFilter(
        field_name="routing_instance__id",
        queryset=models.BGPRoutingInstance.objects.all(),
        to_field_name="id",
        label="BGP Routing Instance ID",
    )

    vrf = django_filters.ModelMultipleChoiceFilter(
        field_name="vrf__name",
        queryset=VRF.objects.all(),
        to_field_name="name",
        label="VRF (name)",
    )

    class Meta:
        model = models.AddressFamily
        fields = [
            "id",
            "routing_instance",
            "afi_safi",
            "vrf",
        ]


class PeerGroupTemplateAddressFamilyFilterSet(
    BaseFilterSet, CreatedUpdatedModelFilterSetMixin, CustomFieldModelFilterSetMixin
):
    """Filtering of PeerGroupTemplateAddressFamily records."""

    q = django_filters.CharFilter(
        method="search",
        label="Search",
    )

    afi_safi = django_filters.MultipleChoiceFilter(choices=choices.AFISAFIChoices)

    peer_group_template = django_filters.ModelMultipleChoiceFilter(
        label="Peer Group Template (ID)",
        queryset=models.PeerGroupTemplate.objects.all(),
    )

    class Meta:
        model = models.PeerGroupTemplateAddressFamily
        fields = [
            "id",
            "afi_safi",
            "peer_group_template",
        ]

    def search(self, queryset, name, value):  # pylint: disable=unused-argument
        """Free-text search method implementation."""
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(afi_safi__icontains=value)
            | Q(peer_group__name__icontains=value)
            | Q(peer_group__description__icontains=value)
        ).distinct()


class PeerGroupAddressFamilyFilterSet(BaseFilterSet, CreatedUpdatedModelFilterSetMixin, CustomFieldModelFilterSetMixin):
    """Filtering of PeerGroupAddressFamily records."""

    q = django_filters.CharFilter(
        method="search",
        label="Search",
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

    def search(self, queryset, name, value):  # pylint: disable=unused-argument
        """Free-text search method implementation."""
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(afi_safi__icontains=value)
            | Q(peer_group__name__icontains=value)
            | Q(peer_group__description__icontains=value)
        ).distinct()


class PeerEndpointAddressFamilyFilterSet(
    BaseFilterSet, CreatedUpdatedModelFilterSetMixin, CustomFieldModelFilterSetMixin
):
    """Filtering of PeerEndpointAddressFamily records."""

    q = django_filters.CharFilter(
        method="search",
        label="Search",
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

    def search(self, queryset, name, value):  # pylint: disable=unused-argument
        """Free-text search method implementation."""
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(afi_safi__icontains=value)
            | Q(peer_endpoint__routing_instance__device__name__iexact=value)
            | Q(peer_endpoint__description__icontains=value)
        ).distinct()
