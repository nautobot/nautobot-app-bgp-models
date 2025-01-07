"""Views for nautobot_bgp_models."""

from nautobot.apps.views import NautobotUIViewSet

from nautobot_bgp_models import filters, forms, models, tables
from nautobot_bgp_models.api import serializers


class AutonomousSystemUIViewSet(NautobotUIViewSet):
    """ViewSet for AutonomousSystem views."""

    bulk_update_form_class = forms.AutonomousSystemBulkEditForm
    filterset_class = filters.AutonomousSystemFilterSet
    filterset_form_class = forms.AutonomousSystemFilterForm
    form_class = forms.AutonomousSystemForm
    lookup_field = "pk"
    queryset = models.AutonomousSystem.objects.all()
    serializer_class = serializers.AutonomousSystemSerializer
    table_class = tables.AutonomousSystemTable
