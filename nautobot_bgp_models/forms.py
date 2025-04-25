"""Forms for nautobot_bgp_models."""

from django import forms
from nautobot.apps.forms import NautobotBulkEditForm, NautobotFilterForm, NautobotModelForm, TagsBulkEditFormMixin

from nautobot_bgp_models import models


class AutonomousSystemForm(NautobotModelForm):  # pylint: disable=too-many-ancestors
    """AutonomousSystem creation/edit form."""

    class Meta:
        """Meta attributes."""

        model = models.AutonomousSystem
        fields = "__all__"


class AutonomousSystemBulkEditForm(TagsBulkEditFormMixin, NautobotBulkEditForm):  # pylint: disable=too-many-ancestors
    """AutonomousSystem bulk edit form."""

    pk = forms.ModelMultipleChoiceField(queryset=models.AutonomousSystem.objects.all(), widget=forms.MultipleHiddenInput)
    description = forms.CharField(required=False)

    class Meta:
        """Meta attributes."""

        nullable_fields = [
            "description",
        ]


class AutonomousSystemFilterForm(NautobotFilterForm):
    """Filter form to filter searches."""

    model = models.AutonomousSystem
    field_order = ["q", "name"]

    q = forms.CharField(
        required=False,
        label="Search",
        help_text="Search within Name.",
    )
    name = forms.CharField(required=False, label="Name")
