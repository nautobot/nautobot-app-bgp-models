# pylint: disable=unsupported-binary-operation
"""FilterSet definitions for nautobot_bgp_models."""

import django_filters
from nautobot.apps.filters import (
    BaseFilterSet,
    CreatedUpdatedModelFilterSetMixin,
    CustomFieldModelFilterSetMixin,
    NautobotFilterSet,
    SearchFilter,
    StatusModelFilterSetMixin,
)
from nautobot.dcim.models import Device
from nautobot.extras.filters.mixins import RoleModelFilterSetMixin
from nautobot.extras.models import Role
from nautobot.ipam.models import VRF

from . import choices, models


class AutonomousSystemFilterSet(NameSearchFilterSet, NautobotFilterSet):  # pylint: disable=too-many-ancestors
    """Filter for AutonomousSystem."""

    class Meta:
        model = models.AutonomousSystem
        fields = ["id", "asn", "status", "tags"]

        # add any fields from the model that you would like to filter your searches by using those
        fields = "__all__"
