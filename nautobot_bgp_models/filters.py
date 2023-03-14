"""FilterSet definitions for nautobot_bgp_models."""

import django_filters

from django.db.models import Q

from nautobot.dcim.models import Device
from nautobot.extras.filters import (
    StatusModelFilterSetMixin,
    CreatedUpdatedFilterSet,
    CustomFieldModelFilterSet,
    RoleModelFilterSetMixin,
)
from nautobot.ipam.models import VRF
from nautobot.apps.filters import BaseFilterSet
from nautobot.core.filters import TagFilter

from . import choices, models


class AutonomousSystemFilterSet(
    BaseFilterSet, CreatedUpdatedFilterSet, CustomFieldModelFilterSet, StatusModelFilterSetMixin
):
    """Filtering of AutonomousSystem records."""

    q = django_filters.CharFilter(
        method="search",
        label="Search",
    )

    tag = TagFilter()

    def search(self, queryset, name, value):  # pylint: disable=unused-argument,no-self-use
        """Free-text search method implementation."""
        if not value.strip():
            return queryset
        return queryset.filter(Q(asn__icontains=value) | Q(description__icontains=value)).distinct()

    class Meta:
        model = models.AutonomousSystem
        fields = ["id", "asn", "status"]


class BGPRoutingInstanceFilterSet(
    BaseFilterSet, CreatedUpdatedFilterSet, CustomFieldModelFilterSet, StatusModelFilterSetMixin
):
    """Filtering of BGPRoutingInstance records."""

    q = django_filters.CharFilter(
        method="search",
        label="Search",
    )

    tag = TagFilter()

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
        fields = ["id", "autonomous_system"]

    def search(self, queryset, name, value):  # pylint: disable=unused-argument,no-self-use
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

    class Meta:
        model = models.PeerGroup
        fields = ["id", "name", "enabled"]

    def search(self, queryset, name, value):  # pylint: disable=unused-argument,no-self-use
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

    def search(self, queryset, name, value):  # pylint: disable=unused-argument,no-self-use
        """Free-text search method implementation."""
        if not value.strip():
            return queryset
        return queryset.filter(Q(name__icontains=value) | Q(description__icontains=value)).distinct()


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

    def search(self, queryset, name, value):  # pylint: disable=unused-argument,no-self-use
        """Free-text search method implementation."""
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(routing_instance__device__name__iexact=value) | Q(description__icontains=value)
        ).distinct()


class PeeringFilterSet(BaseFilterSet, CreatedUpdatedFilterSet, CustomFieldModelFilterSet, StatusModelFilterSetMixin):
    """Filtering of Peering records."""

    # TODO(mzb): Add in-memory filtering for Provider, ASN, IP Address, ...
    #  this requires to consider inheritance methods.

    device = django_filters.ModelMultipleChoiceFilter(
        field_name="endpoints__routing_instance__device__name",
        queryset=Device.objects.all(),
        to_field_name="name",
        label="Device (name)",
    )

    class Meta:
        model = models.Peering
        fields = ["id"]


class AddressFamilyFilterSet(BaseFilterSet, CreatedUpdatedFilterSet, CustomFieldModelFilterSet):
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
