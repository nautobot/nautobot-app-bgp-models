"""Forms and FilterForms for nautobot_bgp_models."""

from django import forms

import nautobot.core.forms as utilities_forms
from nautobot.apps.forms import (
    DynamicModelMultipleChoiceField,
    DynamicModelChoiceField,
    NautobotModelForm,
    NautobotBulkEditForm,
    TagFilterField,
    TagsBulkEditFormMixin,
)
from nautobot.circuits.models import Provider
from nautobot.dcim.models import Device, Interface
from nautobot.extras.forms import NautobotFilterForm, RoleModelFilterFormMixin
from nautobot.extras.models import Tag, Secret, Role
from nautobot.ipam.models import VRF, IPAddress
from nautobot.tenancy.models import Tenant

from . import choices, models


class AutonomousSystemForm(NautobotModelForm):
    """Form for creating/updating AutonomousSystem records."""

    tags = DynamicModelMultipleChoiceField(queryset=Tag.objects.all(), required=False)
    provider = DynamicModelChoiceField(queryset=Provider.objects.all(), required=False)

    class Meta:
        model = models.AutonomousSystem
        fields = ("asn", "description", "provider", "status", "tags")


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

    class Meta:
        model = models.AutonomousSystemRange
        fields = ("name", "asn_min", "asn_max", "description", "tenant", "tags")


class AutonomousSystemRangeFilterForm(NautobotFilterForm):
    """Form for filtering AutonomousSystem records in combination with AutonomousSystemFilterSet."""

    model = models.AutonomousSystemRange
    field_order = ["name", "asn_min", "asn_max", "tenant", "tags"]
    tag = TagFilterField(model)


class AutonomousSystemRangeBulkEditForm(TagsBulkEditFormMixin, NautobotBulkEditForm):
    """Form for bulk-editing multiple AutonomousSystem records."""

    pk = forms.ModelMultipleChoiceField(
        queryset=models.AutonomousSystemRange.objects.all(), widget=forms.MultipleHiddenInput()
    )
    description = forms.CharField(max_length=200, required=False)

    class Meta:
        nullable_fields = [
            "description",
        ]


class BGPRoutingInstanceForm(NautobotModelForm):
    """Form for creating/updating BGPRoutingInstance records."""

    def __init__(self, *args, **kwargs):
        """Init."""
        super().__init__(*args, **kwargs)

        if self.initial.get("device"):
            self.fields["device"].disabled = True
            self.fields.pop("peergroup_template")

    device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
    )

    autonomous_system = DynamicModelChoiceField(
        queryset=models.AutonomousSystem.objects.all(),
    )

    router_id = DynamicModelChoiceField(
        queryset=IPAddress.objects.all(),
        label="Router ID",
        required=False,
        query_params={"device_id": "$device"},
    )

    tags = DynamicModelMultipleChoiceField(queryset=Tag.objects.all(), required=False)

    peergroup_template = DynamicModelMultipleChoiceField(
        queryset=models.PeerGroupTemplate.objects.all(),
        required=False,
        label="Peer Group Templates",
        help_text="Automatically create references to the global peer group templates",
        display_field="name",
    )

    def save(self, commit=True):
        """Save."""
        obj = super().save(commit)

        if commit:
            # Initiate local templates as indicated in the creation form.
            # Templates are only created during object creation.
            for t in self.cleaned_data.get("peergroup_template", []):  # pylint: disable=invalid-name
                models.PeerGroup.objects.create(
                    name=t.name,
                    peergroup_template=t,
                    routing_instance=obj,
                )

        return obj

    class Meta:
        model = models.BGPRoutingInstance
        fields = (
            "device",
            "autonomous_system",
            "status",
            "description",
            "router_id",
            "peergroup_template",
            "tags",
            "extra_attributes",
        )


class BGPRoutingInstanceFilterForm(NautobotFilterForm):
    """Form for filtering BGPRoutingInstance records in combination with BGPRoutingInstanceFilterSet."""

    q = forms.CharField(required=False, label="Search")

    model = models.BGPRoutingInstance

    device = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False,
        to_field_name="name",
    )

    autonomous_system = DynamicModelMultipleChoiceField(
        queryset=models.AutonomousSystem.objects.all(),
        required=False,
        to_field_name="asn",
    )

    tag = TagFilterField(model)

    field_order = [
        "q",
        "device",
        "router_id",
        "autonomous_system",
        "tag",
        "status",
    ]


class BGPRoutingInstanceBulkEditForm(NautobotBulkEditForm):
    """Form for bulk-editing multiple BGPRoutingInstance records."""

    pk = forms.ModelMultipleChoiceField(
        queryset=models.BGPRoutingInstance.objects.all(), widget=forms.MultipleHiddenInput()
    )
    description = forms.CharField(max_length=200, required=False)

    class Meta:
        nullable_fields = [
            "description",
        ]


class PeerGroupForm(NautobotModelForm):
    """Form for creating/updating PeerGroup records."""

    routing_instance = DynamicModelChoiceField(
        queryset=models.BGPRoutingInstance.objects.all(),
        required=True,
        label="BGP Routing Instance",
        help_text="Specify related Routing Instance (Device)",
    )

    vrf = DynamicModelChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label="VRF",
    )

    source_ip = DynamicModelChoiceField(
        queryset=IPAddress.objects.all(),
        required=False,
        label="Source IP Address",
        query_params={
            "nautobot_bgp_models_ips_bgp_routing_instance": "$routing_instance",
            "vrf": "$vrf",
        },
    )

    source_interface = DynamicModelChoiceField(
        queryset=Interface.objects.all(),
        required=False,
        label="Source Interface",
        query_params={"nautobot_bgp_models_interfaces_bgp_routing_instance": "$routing_instance"},
    )

    autonomous_system = DynamicModelChoiceField(
        queryset=models.AutonomousSystem.objects.all(),
        required=False,
        label="Autonomous System",
    )

    peergroup_template = DynamicModelChoiceField(queryset=models.PeerGroupTemplate.objects.all(), required=False)

    secret = DynamicModelChoiceField(queryset=Secret.objects.all(), required=False)

    tags = DynamicModelMultipleChoiceField(queryset=Tag.objects.all(), required=False)

    class Meta:
        model = models.PeerGroup
        fields = (
            "routing_instance",
            "name",
            "vrf",
            "peergroup_template",
            "description",
            "enabled",
            "role",
            "source_ip",
            "source_interface",
            "autonomous_system",
            "secret",
            "extra_attributes",
            "tags",
        )


class PeerGroupBulkEditForm(NautobotBulkEditForm):
    """Form for bulk-editing multiple PeerGroup records."""

    pk = forms.ModelMultipleChoiceField(
        queryset=models.PeerGroupTemplate.objects.all(), widget=forms.MultipleHiddenInput()
    )
    description = forms.CharField(max_length=200, required=False)

    class Meta:
        nullable_fields = [
            "description",
        ]


class PeerGroupTemplateForm(NautobotModelForm):
    """Form for creating/updating PeerGroup records."""

    autonomous_system = DynamicModelChoiceField(
        queryset=models.AutonomousSystem.objects.all(),
        required=False,
        label="Autonomous System",
    )

    secret = DynamicModelChoiceField(queryset=Secret.objects.all(), required=False)

    class Meta:
        model = models.PeerGroupTemplate
        fields = (
            "name",
            "description",
            "enabled",
            "role",
            "autonomous_system",
            "extra_attributes",
            "tags",
        )


class PeerGroupTemplateBulkEditForm(NautobotBulkEditForm):
    """Form for bulk-editing multiple PeerGroupTemplate records."""

    pk = forms.ModelMultipleChoiceField(
        queryset=models.PeerGroupTemplate.objects.all(), widget=forms.MultipleHiddenInput()
    )
    description = forms.CharField(max_length=200, required=False)

    class Meta:
        nullable_fields = [
            "description",
        ]


class PeerGroupFilterForm(NautobotFilterForm, RoleModelFilterFormMixin):
    """Form for filtering PeerGroup records in combination with PeerGroupFilterSet."""

    model = models.PeerGroup

    q = forms.CharField(required=False, label="Search")

    enabled = forms.NullBooleanField(
        required=False, widget=utilities_forms.StaticSelect2(choices=utilities_forms.BOOLEAN_WITH_BLANK_CHOICES)
    )

    autonomous_system = DynamicModelMultipleChoiceField(
        queryset=models.AutonomousSystem.objects.all(), to_field_name="asn", required=False
    )

    vrf = DynamicModelMultipleChoiceField(queryset=VRF.objects.all(), required=False)


class PeerGroupTemplateFilterForm(NautobotFilterForm, RoleModelFilterFormMixin):
    """Form for filtering PeerGroupTemplate records in combination with PeerGroupTemplateFilterSet."""

    model = models.PeerGroup

    q = forms.CharField(required=False, label="Search")

    enabled = forms.NullBooleanField(
        required=False, widget=utilities_forms.StaticSelect2(choices=utilities_forms.BOOLEAN_WITH_BLANK_CHOICES)
    )

    autonomous_system = DynamicModelMultipleChoiceField(
        queryset=models.AutonomousSystem.objects.all(), to_field_name="asn", required=False
    )


class PeerEndpointForm(NautobotModelForm):
    """Form for creating/updating PeerEndpoint records."""

    def __init__(self, *args, **kwargs):
        """Init."""
        super().__init__(*args, **kwargs)

        if self.initial.get("routing_instance"):
            self.fields["routing_instance"].disabled = True

        _prefix = f"{self.prefix}-" if self.prefix else ""
        self.fields["source_ip"].widget.add_query_param(
            "nautobot_bgp_models_ips_bgp_routing_instance", f"${_prefix}routing_instance"
        )
        self.fields["source_interface"].widget.add_query_param(
            "nautobot_bgp_models_interfaces_bgp_routing_instance", f"${_prefix}routing_instance"
        )
        self.fields["peer_group"].widget.add_query_param("routing_instance", f"${_prefix}routing_instance")

    routing_instance = DynamicModelChoiceField(
        queryset=models.BGPRoutingInstance.objects.all(),
        required=False,
        label="BGP Routing Instance",
        help_text="Specify related Routing Instance (Device)",
    )

    autonomous_system = DynamicModelChoiceField(
        queryset=models.AutonomousSystem.objects.all(),
        required=False,
        label="Autonomous System",
    )

    source_ip = DynamicModelChoiceField(
        queryset=IPAddress.objects.all(),
        required=False,
        label="Source IP Address",
    )

    source_interface = DynamicModelChoiceField(
        queryset=Interface.objects.all(),
        required=False,
        label="Source Interface",
    )

    peer_group = DynamicModelChoiceField(
        queryset=models.PeerGroup.objects.all(),
        required=False,
        label="Peer Group",
    )

    secret = DynamicModelChoiceField(queryset=Secret.objects.all(), required=False)

    peering = DynamicModelChoiceField(  # Hidden & optional - update peers manually for new peerings.
        queryset=models.Peering.objects.all(),
        widget=forms.HiddenInput(),
        required=False,
    )

    tags = DynamicModelMultipleChoiceField(queryset=Tag.objects.all(), required=False)

    class Meta:
        model = models.PeerEndpoint
        fields = (
            "peering",
            "routing_instance",
            "description",
            "enabled",
            "role",
            "source_ip",
            "source_interface",
            "autonomous_system",
            "peer_group",
            "secret",
            "extra_attributes",
            "tags",
        )

    def save(self, commit=True):
        """Save model changes on successful form submission."""
        endpoint = super().save(commit=commit)

        if commit:
            endpoint.peering.update_peers()

        return endpoint


class PeerEndpointFilterForm(NautobotFilterForm, RoleModelFilterFormMixin):
    """Form for filtering PeerEndpoint records in combination with PeerEndpointFilterSet."""

    model = models.PeerEndpoint
    tag = TagFilterField(model)


class PeerEndpointBulkEditForm(NautobotBulkEditForm):
    """Form for bulk-editing multiple PeerEndpoint records."""

    pk = forms.ModelMultipleChoiceField(queryset=models.PeerEndpoint.objects.all(), widget=forms.MultipleHiddenInput())

    class Meta:
        nullable_fields = []


class PeeringForm(NautobotModelForm):
    """Form for creating/updating Peering records."""

    class Meta:
        model = models.Peering
        fields = ("status",)


class PeeringFilterForm(NautobotFilterForm):
    """Form for filtering Peering records in combination with PeeringFilterSet."""

    model = models.Peering
    field_order = [
        "q",
        "status",
        "device",
        "device_role",
        "peer_endpoint_role",
    ]

    device = DynamicModelMultipleChoiceField(queryset=Device.objects.all(), to_field_name="name", required=False)

    device_role = DynamicModelMultipleChoiceField(
        queryset=Role.objects.all(),
        to_field_name="name",
        required=False,
    )

    peer_endpoint_role = DynamicModelMultipleChoiceField(
        queryset=Role.objects.all(), to_field_name="name", required=False
    )


class AddressFamilyForm(NautobotModelForm):
    """Form for creating/updating AddressFamily records."""

    routing_instance = DynamicModelChoiceField(
        queryset=models.BGPRoutingInstance.objects.all(),
        required=True,
        label="BGP Routing Instance",
        help_text="Specify related Routing Instance (Device)",
    )

    afi_safi = forms.ChoiceField(
        label="AFI-SAFI",
        choices=choices.AFISAFIChoices,
        required=False,
        widget=utilities_forms.StaticSelect2(),
    )

    vrf = DynamicModelChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label="VRF",
    )

    class Meta:
        model = models.AddressFamily
        fields = (
            "routing_instance",
            "afi_safi",
            "vrf",
            "extra_attributes",
        )


class AddressFamilyBulkEditForm(NautobotBulkEditForm):
    """Form for bulk-editing multiple AddressFamily records."""

    pk = forms.ModelMultipleChoiceField(queryset=models.AddressFamily.objects.all(), widget=forms.MultipleHiddenInput())

    class Meta:
        nullable_fields = []


class AddressFamilyFilterForm(NautobotFilterForm):
    """Form for filtering AddressFamily records in combination with AddressFamilyFilterSet."""

    model = models.AddressFamily

    routing_instance = DynamicModelMultipleChoiceField(queryset=models.BGPRoutingInstance.objects.all(), required=False)

    afi_safi = forms.MultipleChoiceField(
        label="AFI-SAFI",
        choices=choices.AFISAFIChoices,
        required=False,
        widget=utilities_forms.StaticSelect2Multiple(),
    )

    vrf = DynamicModelMultipleChoiceField(queryset=VRF.objects.all(), required=False)


class PeerGroupAddressFamilyForm(NautobotModelForm):
    """Form for creating/updating PeerGroupAddressFamily records."""

    peer_group = DynamicModelChoiceField(
        queryset=models.PeerGroup.objects.all(),
        required=True,
        label="BGP Peer Group",
    )

    afi_safi = forms.ChoiceField(
        label="AFI-SAFI",
        choices=choices.AFISAFIChoices,
        required=False,
        widget=utilities_forms.StaticSelect2(),
    )

    multipath = forms.NullBooleanField(required=False, widget=utilities_forms.BulkEditNullBooleanSelect())

    class Meta:
        model = models.PeerGroupAddressFamily
        fields = (
            "peer_group",
            "afi_safi",
            "import_policy",
            "export_policy",
            "multipath",
            "extra_attributes",
        )


class PeerGroupAddressFamilyBulkEditForm(NautobotBulkEditForm):
    """Form for bulk-editing multiple PeerGroupAddressFamily records."""

    pk = forms.ModelMultipleChoiceField(
        queryset=models.PeerGroupAddressFamily.objects.all(), widget=forms.MultipleHiddenInput()
    )
    import_policy = forms.CharField(max_length=100, required=False)
    export_policy = forms.CharField(max_length=100, required=False)
    multipath = forms.NullBooleanField(required=False, widget=utilities_forms.BulkEditNullBooleanSelect())

    class Meta:
        nullable_fields = ["import_policy", "export_policy", "multipath"]


class PeerGroupAddressFamilyFilterForm(NautobotFilterForm):
    """Form for filtering PeerGroupAddressFamily records in combination with PeerGroupAddressFamilyFilterSet."""

    model = models.PeerGroupAddressFamily

    peer_group = DynamicModelMultipleChoiceField(queryset=models.PeerGroup.objects.all(), required=False)

    afi_safi = forms.MultipleChoiceField(
        label="AFI-SAFI",
        choices=choices.AFISAFIChoices,
        required=False,
        widget=utilities_forms.StaticSelect2Multiple(),
    )


class PeerEndpointAddressFamilyForm(NautobotModelForm):
    """Form for creating/updating PeerEndpointAddressFamily records."""

    peer_endpoint = DynamicModelChoiceField(
        queryset=models.PeerEndpoint.objects.all(),
        required=True,
        label="BGP Peer Endpoint",
    )

    afi_safi = forms.ChoiceField(
        label="AFI-SAFI",
        choices=choices.AFISAFIChoices,
        required=False,
        widget=utilities_forms.StaticSelect2(),
    )

    multipath = forms.NullBooleanField(required=False, widget=utilities_forms.BulkEditNullBooleanSelect())

    class Meta:
        model = models.PeerGroupAddressFamily
        fields = (
            "peer_endpoint",
            "afi_safi",
            "import_policy",
            "export_policy",
            "multipath",
            "extra_attributes",
        )


class PeerEndpointAddressFamilyBulkEditForm(NautobotBulkEditForm):
    """Form for bulk-editing multiple PeerEndpointAddressFamily records."""

    pk = forms.ModelMultipleChoiceField(
        queryset=models.PeerEndpointAddressFamily.objects.all(), widget=forms.MultipleHiddenInput()
    )
    import_policy = forms.CharField(max_length=100, required=False)
    export_policy = forms.CharField(max_length=100, required=False)
    multipath = forms.NullBooleanField(required=False, widget=utilities_forms.BulkEditNullBooleanSelect())

    class Meta:
        nullable_fields = ["import_policy", "export_policy", "multipath"]


class PeerEndpointAddressFamilyFilterForm(NautobotFilterForm):
    """Form for filtering PeerEndpointAddressFamily records in combination with PeerEndpointAddressFamilyFilterSet."""

    model = models.PeerEndpointAddressFamily

    peer_endpoint = DynamicModelMultipleChoiceField(queryset=models.PeerEndpoint.objects.all(), required=False)

    afi_safi = forms.MultipleChoiceField(
        label="AFI-SAFI",
        choices=choices.AFISAFIChoices,
        required=False,
        widget=utilities_forms.StaticSelect2Multiple(),
    )
