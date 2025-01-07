"""API serializers for nautobot_bgp_models."""

from nautobot.apps.api import NautobotModelSerializer, TaggedModelSerializerMixin

from nautobot_bgp_models import models


class AutonomousSystemSerializer(NautobotModelSerializer, TaggedModelSerializerMixin):  # pylint: disable=too-many-ancestors
    """AutonomousSystem Serializer."""

    class Meta:
        """Meta attributes."""

        model = models.AutonomousSystem
        fields = "__all__"

        # Option for disabling write for certain fields:
        # read_only_fields = []
