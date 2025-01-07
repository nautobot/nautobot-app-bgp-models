"""Filtering for nautobot_bgp_models."""

from nautobot.apps.filters import NameSearchFilterSet, NautobotFilterSet

from nautobot_bgp_models import models


class AutonomousSystemFilterSet(NautobotFilterSet, NameSearchFilterSet):  # pylint: disable=too-many-ancestors
    """Filter for AutonomousSystem."""

    class Meta:
        """Meta attributes for filter."""

        model = models.AutonomousSystem

        # add any fields from the model that you would like to filter your searches by using those
        fields = ["id", "name", "description"]
