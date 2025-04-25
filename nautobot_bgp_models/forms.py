"""Forms and FilterForms for nautobot_bgp_models."""

import nautobot.core.forms as utilities_forms
from django import forms
from nautobot.apps.forms import (
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    NautobotBulkEditForm,
    NautobotModelForm,
    TagFilterField,
    TagsBulkEditFormMixin,
)
from nautobot.circuits.models import Provider
from nautobot.dcim.models import Device, Interface
from nautobot.extras.forms import NautobotFilterForm, RoleModelFilterFormMixin
from nautobot.extras.models import Role, Secret, Tag
from nautobot.ipam.models import VRF, IPAddress
from nautobot.tenancy.models import Tenant

from . import choices, models


class AutonomousSystemForm(NautobotModelForm):
    """Form for creating/updating AutonomousSystem records."""

    tags = DynamicModelMultipleChoiceField(queryset=Tag.objects.all(), required=False)
    provider = DynamicModelChoiceField(queryset=Provider.objects.all(), required=False)

    class Meta:
        model = models.AutonomousSystem
        fields = "__all__"


class AutonomousSystemFilterForm(NautobotFilterForm):
    """Form for filtering AutonomousSystem records in combination with AutonomousSystemFilterSet."""

    model = models.AutonomousSystem
    field_order = ["status", "tag"]
    tag = TagFilterField(model)


class AutonomousSystemBulkEditForm(TagsBulkEditFormMixin, NautobotBulkEditForm):
    """Form for bulk-editing multiple AutonomousSystem records."""

    pk = forms.ModelMultipleChoiceField(
        queryset=models.AutonomousSystem.objects.all(), widget=forms.MultipleHiddenInput()
    )
    description = forms.CharField(max_length=200, required=False)

    class Meta:
        nullable_fields = [
            "description",
        ]


class AutonomousSystemRangeForm(NautobotModelForm):
    """Form for creating/updating AutonomousSystem records."""

    tags = DynamicModelMultipleChoiceField(queryset=Tag.objects.all(), required=False)
    tenant = DynamicModelChoiceField(queryset=Tenant.objects.all(), required=False)

    q = forms.CharField(
        required=False,
        label="Search",
        help_text="Search within Name.",
    )
