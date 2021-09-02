"""Forms and FilterForms for nautobot_bgp_models."""

from django import forms

from nautobot.dcim.models import Device, Interface
from nautobot.extras.models import Tag
import nautobot.extras.forms as extras_forms
from nautobot.ipam.models import VRF, IPAddress
import nautobot.utilities.forms as utilities_forms
from nautobot.virtualization.models import VMInterface

from . import choices, models


class AutonomousSystemForm(
    utilities_forms.BootstrapMixin, extras_forms.CustomFieldModelForm, extras_forms.RelationshipModelForm
):
    """Form for creating/updating AutonomousSystem records."""

    tags = utilities_forms.DynamicModelMultipleChoiceField(queryset=Tag.objects.all(), required=False)

    class Meta:
        model = models.AutonomousSystem
        fields = ("asn", "description", "status", "tags")


class AutonomousSystemFilterForm(
    utilities_forms.BootstrapMixin, extras_forms.StatusFilterFormMixin, extras_forms.CustomFieldFilterForm
):
    """Form for filtering AutonomousSystem records in combination with AutonomousSystemFilterSet."""

    model = models.AutonomousSystem
    field_order = ["status", "tag"]
    tag = utilities_forms.TagFilterField(model)


class AutonomousSystemCSVForm(extras_forms.StatusModelCSVFormMixin, extras_forms.CustomFieldModelCSVForm):
    """Form for importing AutonomousSystems from CSV data."""

    class Meta:
        model = models.AutonomousSystem
        fields = models.AutonomousSystem.csv_headers


class AutonomousSystemBulkEditForm(
    utilities_forms.BootstrapMixin, extras_forms.AddRemoveTagsForm, extras_forms.CustomFieldBulkEditForm
):
    """Form for bulk-editing multiple AutonomousSystem records."""

    pk = forms.ModelMultipleChoiceField(
        queryset=models.AutonomousSystem.objects.all(), widget=forms.MultipleHiddenInput()
    )
    description = forms.CharField(max_length=200, required=False)

    class Meta:
        nullable_fields = [
            "description",
        ]


class PeeringRoleForm(
    utilities_forms.BootstrapMixin, extras_forms.CustomFieldModelForm, extras_forms.RelationshipModelForm
):
    """Form for creating/updating PeeringRole records."""

    slug = utilities_forms.SlugField()

    class Meta:
        model = models.PeeringRole
        fields = ("name", "slug", "color", "description")


class PeeringRoleFilterForm(utilities_forms.BootstrapMixin, extras_forms.CustomFieldFilterForm):
    """Form for filtering PeeringRole records in combination with PeeringRoleFilterSet."""

    model = models.PeeringRole
    q = forms.CharField(required=False, label="Search")
    color = forms.CharField(max_length=6, required=False, widget=utilities_forms.ColorSelect())


class PeeringRoleCSVForm(extras_forms.CustomFieldModelCSVForm):
    """Form for importing PeeringRole records from CSV data."""

    class Meta:
        model = models.PeeringRole
        fields = models.PeeringRole.csv_headers


class PeeringRoleBulkEditForm(utilities_forms.BootstrapMixin, extras_forms.CustomFieldBulkEditForm):
    """Form for bulk-editing multiple PeeringRole records."""

    pk = forms.ModelMultipleChoiceField(queryset=models.PeeringRole.objects.all(), widget=forms.MultipleHiddenInput())
    color = forms.CharField(max_length=6, required=False, widget=utilities_forms.ColorSelect())
    description = forms.CharField(max_length=200, required=False)

    class Meta:
        nullable_fields = [
            "description",
        ]


class AbstractPeeringInfoForm(
    utilities_forms.BootstrapMixin, extras_forms.CustomFieldModelForm, extras_forms.RelationshipModelForm
):
    """Abstract parent of PeerGroupForm and PeeringEndpointForm."""

    update_source_interface = utilities_forms.DynamicModelChoiceField(
        queryset=Interface.objects.all(),
        required=False,
        query_params={"device_id": "$device"},
        label="Update source",
    )
    update_source_vminterface = utilities_forms.DynamicModelChoiceField(
        queryset=VMInterface.objects.all(),
        required=False,
        query_params={"virtual_machine_id": "$virtual_machine"},
        label="Update source",
    )

    router_id = utilities_forms.DynamicModelChoiceField(
        queryset=IPAddress.objects.all(),
        required=False,
        label="Router ID",
    )

    bfd_fast_detection = forms.NullBooleanField(
        required=False, widget=utilities_forms.BulkEditNullBooleanSelect(), label="BFD fast-detection"
    )
    enforce_first_as = forms.NullBooleanField(
        required=False, widget=utilities_forms.BulkEditNullBooleanSelect(), label="Enforce first AS"
    )
    send_community_ebgp = forms.NullBooleanField(
        required=False, widget=utilities_forms.BulkEditNullBooleanSelect(), label="Send-community eBGP"
    )

    class Meta:
        fields = (
            "description",
            "enabled",
            "vrf",
            "update_source_interface",
            "update_source_vminterface",
            "router_id",
            "autonomous_system",
            "maximum_paths_ibgp",
            "maximum_paths_ebgp",
            "maximum_paths_eibgp",
            "maximum_prefix",
            "bfd_multiplier",
            "bfd_minimum_interval",
            "bfd_fast_detection",
            "enforce_first_as",
            "send_community_ebgp",
        )

    def __init__(self, *args, **kwargs):
        """Set up initial data for this form."""
        instance = kwargs.get("instance")
        initial = kwargs.get("initial", {}).copy()

        if instance:
            if isinstance(instance.update_source, Interface):
                initial["update_source_interface"] = instance.update_source
            elif isinstance(instance.update_source, VMInterface):
                initial["update_source_vminterface"] = instance.update_source

        kwargs["initial"] = initial

        super().__init__(*args, **kwargs)

    def clean(self):
        """Form validation logic."""
        super().clean()

        if self.cleaned_data.get("update_source_interface") and self.cleaned_data.get("update_source_vminterface"):
            raise forms.ValidationError(
                "Cannot select both a device interface and a virtual machine interface as update-source"
            )
        self.instance.update_source = self.cleaned_data.get("update_source_interface") or self.cleaned_data.get(
            "update_source_vminterface"
        )


class PeerGroupForm(AbstractPeeringInfoForm):
    """Form for creating/updating PeerGroup records."""

    class Meta:
        model = models.PeerGroup
        fields = (
            "name",
            "role",
            *AbstractPeeringInfoForm.Meta.fields,
        )


class AbstractPeeringInfoFilterForm(utilities_forms.BootstrapMixin, extras_forms.CustomFieldFilterForm):
    """Abstract parent class of PeerGroupFilterForm and PeerEndpointFilterForm."""

    q = forms.CharField(required=False, label="Search")
    enabled = forms.NullBooleanField(
        required=False, widget=utilities_forms.StaticSelect2(choices=utilities_forms.BOOLEAN_WITH_BLANK_CHOICES)
    )
    vrf = utilities_forms.DynamicModelMultipleChoiceField(
        queryset=VRF.objects.all(), to_field_name="name", required=False, label="VRF"
    )
    autonomous_system = utilities_forms.DynamicModelMultipleChoiceField(
        queryset=models.AutonomousSystem.objects.all(), to_field_name="asn", required=False
    )


class PeerGroupFilterForm(AbstractPeeringInfoFilterForm):
    """Form for filtering PeerGroup records in combination with PeerGroupFilterSet."""

    model = models.PeerGroup
    # TODO filter by device/virtual machine
    role = utilities_forms.DynamicModelMultipleChoiceField(
        queryset=models.PeeringRole.objects.all(), to_field_name="slug", required=False
    )


class PeerEndpointForm(AbstractPeeringInfoForm):
    """Form for creating/updating PeerEndpoint records."""

    autonomous_system = utilities_forms.DynamicModelChoiceField(
        queryset=models.AutonomousSystem.objects.all(),
        required=False,
        help_text="Required if the Local IP is not associated with a Device",
    )

    local_ip = utilities_forms.DynamicModelChoiceField(
        queryset=IPAddress.objects.all(),
        required=True,
        label="Local IP Address",
    )

    peer_group = utilities_forms.DynamicModelChoiceField(
        queryset=models.PeerGroup.objects.all(),
        required=False,
        label="Peer Group",
    )

    class Meta:
        model = models.PeerEndpoint
        fields = (
            "peer_group",
            "local_ip",
            *AbstractPeeringInfoForm.Meta.fields,
        )

    def save(self, commit=True):
        """Save model changes on successful form submission."""
        endpoint = super().save(commit=commit)

        if commit:
            endpoint.session.update_peers()

        return endpoint


class PeerEndpointFilterForm(AbstractPeeringInfoFilterForm):
    """Form for filtering PeerEndpoint records in combination with PeerEndpointFilterSet."""

    model = models.PeerEndpoint
    # TODO: filtering by device/virtual machine
    peer_group = utilities_forms.DynamicModelMultipleChoiceField(
        queryset=models.PeerGroup.objects.all(), required=False
    )


class PeerSessionForm(
    utilities_forms.BootstrapMixin, extras_forms.CustomFieldModelForm, extras_forms.RelationshipModelForm
):
    """Form for creating/updating PeerSession records."""

    class Meta:
        model = models.PeerSession
        fields = (
            "role",
            "status",
            "authentication_key",
        )


class PeerSessionFilterForm(
    utilities_forms.BootstrapMixin, extras_forms.StatusFilterFormMixin, extras_forms.CustomFieldFilterForm
):
    """Form for filtering PeerSession records in combination with PeerSessionFilterSet."""

    model = models.PeerSession
    field_order = [
        "q",
        "role",
        "status",
        "address",
        "device",
        "asn",
    ]
    role = utilities_forms.DynamicModelMultipleChoiceField(
        queryset=models.PeeringRole.objects.all(), to_field_name="slug", required=False
    )

    address = forms.CharField(required=False, label="Address")

    device = utilities_forms.DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(), to_field_name="name", required=False
    )

    asn = utilities_forms.DynamicModelMultipleChoiceField(
        queryset=models.AutonomousSystem.objects.all(), to_field_name="asn", required=False
    )


class AddressFamilyForm(
    utilities_forms.BootstrapMixin, extras_forms.CustomFieldModelForm, extras_forms.RelationshipModelForm
):
    """Form for creating/updating AddressFamily records."""

    multipath = forms.NullBooleanField(required=False, widget=utilities_forms.BulkEditNullBooleanSelect())

    peer_group = utilities_forms.DynamicModelChoiceField(
        queryset=models.PeerGroup.objects.all(),
        required=False,
        label="Peer Group",
    )

    peer_endpoint = utilities_forms.DynamicModelChoiceField(
        queryset=models.PeerEndpoint.objects.all(),
        required=False,
        label="Peer Endpoint",
    )

    class Meta:
        model = models.AddressFamily
        fields = (
            "afi_safi",
            "peer_group",
            "peer_endpoint",
            "import_policy",
            "export_policy",
            "redistribute_static_policy",
            "maximum_prefix",
            "multipath",
        )


class AddressFamilyFilterForm(utilities_forms.BootstrapMixin, extras_forms.CustomFieldFilterForm):
    """Form for filtering AddressFamily records in combination with AddressFamilyFilterSet."""

    model = models.AddressFamily
    afi_safi = forms.MultipleChoiceField(
        label="AFI-SAFI",
        choices=choices.AFISAFIChoices,
        required=False,
        widget=utilities_forms.StaticSelect2Multiple(),
    )

    peer_group = utilities_forms.DynamicModelMultipleChoiceField(
        queryset=models.PeerGroup.objects.all(), required=False
    )
    peer_endpoint = utilities_forms.DynamicModelMultipleChoiceField(
        queryset=models.PeerEndpoint.objects.all(), required=False
    )
