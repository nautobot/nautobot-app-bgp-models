"""FilterSet definitions for nautobot_bgp_models."""

import django_filters

from django.db.models import Q

from nautobot.extras.filters import StatusModelFilterSetMixin, CreatedUpdatedFilterSet, CustomFieldModelFilterSet
from nautobot.ipam.models import VRF
from nautobot.utilities.filters import BaseFilterSet, NameSlugSearchFilterSet, TagFilter

from . import choices, models


class AutonomousSystemFilterSet(
    BaseFilterSet, CreatedUpdatedFilterSet, CustomFieldModelFilterSet, StatusModelFilterSetMixin
):
    """Filtering of AutonomousSystem records."""

    tag = TagFilter()

    class Meta:
        model = models.AutonomousSystem
        fields = ["id", "asn", "status"]


class PeeringRoleFilterSet(BaseFilterSet, CreatedUpdatedFilterSet, CustomFieldModelFilterSet, NameSlugSearchFilterSet):
    """Filtering of PeeringRole records."""

    q = django_filters.CharFilter(
        method="search",
        label="Search",
    )

    class Meta:
        model = models.PeeringRole
        fields = ["id", "name", "slug", "color", "description"]

    def search(self, queryset, name, value):  # pylint: disable=unused-argument,no-self-use
        """Free-text search method implementation."""
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) | Q(slug__icontains=value) | Q(description__icontains=value)
        ).distinct()


class AbstractPeeringInfoFilterSet(CreatedUpdatedFilterSet, CustomFieldModelFilterSet):
    """Abstract parent of PeerGroupFilterSet and PeerEndpointFilterSet."""

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
    vrf = django_filters.ModelMultipleChoiceFilter(
        field_name="vrf__name",
        queryset=VRF.objects.all(),
        to_field_name="name",
        label="VRF (name)",
    )

    class Meta:
        abstract = True


class PeerGroupFilterSet(BaseFilterSet, AbstractPeeringInfoFilterSet):
    """Filtering of PeerGroup records."""

    # TODO filtering on device (Device | VirtualMachine)
    role = django_filters.ModelMultipleChoiceFilter(
        field_name="role__slug",
        queryset=models.PeeringRole.objects.all(),
        to_field_name="slug",
        label="Peering role (slug)",
    )

    class Meta:
        model = models.PeerGroup
        fields = ["id", "name", "enabled"]

    def search(self, queryset, name, value):  # pylint: disable=unused-argument,no-self-use
        """Free-text search method implementation."""
        if not value.strip():
            return queryset
        return queryset.filter(Q(name__icontains=value) | Q(description__icontains=value)).distinct()


class PeerEndpointFilterSet(BaseFilterSet, AbstractPeeringInfoFilterSet):
    """Filtering of PeerEndpoint records."""

    # TODO: filtering on device (Device | VirtualMachine)
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
            # TODO we should search on device names too
            Q(peer_group__name__icontains=value)
        ).distinct()


class PeerSessionFilterSet(
    BaseFilterSet, CreatedUpdatedFilterSet, CustomFieldModelFilterSet, StatusModelFilterSetMixin
):
    """Filtering of PeerSession records."""

    role = django_filters.ModelMultipleChoiceFilter(
        field_name="role__slug",
        queryset=models.PeeringRole.objects.all(),
        to_field_name="slug",
        label="Peering role (slug)",
    )

    class Meta:
        model = models.PeerSession
        fields = ["id"]


class AddressFamilyFilterSet(BaseFilterSet, CreatedUpdatedFilterSet, CustomFieldModelFilterSet):
    """Filtering of AddressFamily records."""

    afi_safi = django_filters.MultipleChoiceFilter(choices=choices.AFISAFIChoices)
    # TODO: filtering on device (Device | VirtualMachine)
    peer_group = django_filters.ModelMultipleChoiceFilter(
        queryset=models.PeerGroup.objects.all(),
        label="Peer Group (id)",
    )
    peer_endpoint = django_filters.ModelMultipleChoiceFilter(
        queryset=models.PeerEndpoint.objects.all(),
        label="Peer Endpoint (id)",
    )

    class Meta:
        model = models.AddressFamily
        fields = ["id", "afi_safi"]
