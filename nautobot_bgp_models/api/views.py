"""API views for nautobot_bgp_models."""

from nautobot.apps.api import NautobotModelViewSet

from nautobot_bgp_models import filters, models
from nautobot_bgp_models.api import serializers


class AutonomousSystemViewSet(NautobotModelViewSet):  # pylint: disable=too-many-ancestors
    """AutonomousSystem viewset."""

    queryset = models.AutonomousSystem.objects.all()
    serializer_class = serializers.AutonomousSystemSerializer
    filterset_class = filters.AutonomousSystemFilterSet

    # Option for modifying the default HTTP methods:
    # http_method_names = ["get", "post", "put", "patch", "delete", "head", "options", "trace"]
