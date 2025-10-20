"""View classes for nautobot_bgp_models."""

from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import redirect, render
from django.utils.html import format_html
from django_tables2 import RequestConfig
from nautobot.apps.choices import ButtonActionIconChoices
from nautobot.apps.ui import (
    Button,
    ButtonColorChoices,
    DropdownButton,
    ObjectDetailContent,
    ObjectFieldsPanel,
    ObjectsTablePanel,
    ObjectTextPanel,
    SectionChoices,
    Tab,
)
from nautobot.apps.views import (
    EnhancedPaginator,
    NautobotUIViewSet,
    ObjectBulkDestroyViewMixin,
    ObjectChangeLogViewMixin,
    ObjectDestroyViewMixin,
    ObjectDetailViewMixin,
    ObjectEditView,
    ObjectEditViewMixin,
    ObjectListViewMixin,
    ObjectNotesViewMixin,
    get_obj_from_context,
    get_paginate_count,
)

from . import filters, forms, helpers, models, tables
from .api import serializers


class BGPObjectsFieldPanel(ObjectFieldsPanel):
    """Object detail panel for BGP objects."""

    def render_value(self, key, value, context):
        """Wrapper to swap for inherited values and display inheritance information."""
        obj = get_obj_from_context(context, self.context_object_key)

        if not hasattr(obj, "property_inheritance"):
            return super().render_value(key, value, context)

        if key not in obj.property_inheritance:
            return super().render_value(key, value, context)

        value, inheritance_indicator, inheritance_source = obj.get_inherited_field(
            field_name=key,
            inheritance_path=obj.property_inheritance[key],
        )

        rendered_value = super().render_value(key, value, context)

        if inheritance_indicator:
            rendered_value = rendered_value + format_html(
                """ <a href="{url}" class="btn btn-xs btn-info">
                    <span class="mdi mdi-content-duplicate" aria-hidden="true"></span> {source_obj}
                    </a>
                """,
                url=inheritance_source.get_absolute_url(),
                source_obj=inheritance_source,
            )

        return rendered_value


extra_attributes_tab = Tab(
    weight=100,
    tab_id="extra_attributes",
    label="Extra Attributes",
    panels=[
        ObjectTextPanel(
            weight=100,
            section=SectionChoices.LEFT_HALF,
            label="Rendered BGP Extra Attributes (includes inherited)",
            object_field="extra_attributes",
            render_as=ObjectTextPanel.RenderOptions.JSON,
        ),
        ObjectTextPanel(
            weight=100,
            section=SectionChoices.RIGHT_HALF,
            label="BGP object's extra attributes (The local BGP object's extra attribute overwrite all inherited attributes.)",
            object_field="extra_attributes_inherited",
            render_as=ObjectTextPanel.RenderOptions.JSON,
        ),
    ],
)


class AutonomousSystemUIViewSet(NautobotUIViewSet):
    """UIViewset for AutonomousSystem model."""

    bulk_update_form_class = forms.AutonomousSystemBulkEditForm
    filterset_class = filters.AutonomousSystemFilterSet
    filterset_form_class = forms.AutonomousSystemFilterForm
    form_class = forms.AutonomousSystemForm
    lookup_field = "pk"
    queryset = models.AutonomousSystem.objects.all()
    serializer_class = serializers.AutonomousSystemSerializer
    table_class = tables.AutonomousSystemTable

    object_detail_content = ObjectDetailContent(
        panels=[
            ObjectFieldsPanel(
                weight=100,
                section=SectionChoices.LEFT_HALF,
                fields=["asn", "asn_asdot", "description", "status", "provider"],
            ),
        ],
    )


class AutonomousSystemRangeUIViewSet(NautobotUIViewSet):
    """UIViewset for AutonomousSystemRange model."""

    bulk_update_form_class = forms.AutonomousSystemRangeBulkEditForm
    filterset_class = filters.AutonomousSystemRangeFilterSet
    filterset_form_class = forms.AutonomousSystemRangeFilterForm
    form_class = forms.AutonomousSystemRangeForm
    lookup_field = "pk"
    queryset = models.AutonomousSystemRange.objects.all()
    serializer_class = serializers.AutonomousSystemRangeSerializer
    table_class = tables.AutonomousSystemRangeTable

    object_detail_content = ObjectDetailContent(
        panels=[
            ObjectFieldsPanel(
                weight=100,
                section=SectionChoices.LEFT_HALF,
                fields="__all__",
            ),
            ObjectsTablePanel(
                section=SectionChoices.RIGHT_HALF,
                weight=100,
                context_table_key="asn_range_table",
                show_table_config_button=False,
                paginate=False,
            ),
        ],
    )

    def get_extra_context(self, request, instance):  # pylint: disable=signature-differs
        """Return any additional context data for the template."""
        context = super().get_extra_context(request, instance)
        if self.action == "retrieve":
            asns = models.AutonomousSystem.objects.filter(asn__gte=instance.asn_min, asn__lte=instance.asn_max)
            asns = helpers.add_available_asns(instance, asns)

            asn_table = tables.AutonomousSystemTable(asns)
            asn_table.columns.hide("actions")

            if request.user.has_perm("nautobot_bgp_models.change_autonomoussystem") or request.user.has_perm(
                "nautobot_bgp_models.delete_autonomoussystem"
            ):
                asn_table.columns.show("pk")

            paginate = {
                "paginator_class": EnhancedPaginator,
                "per_page": get_paginate_count(request),
            }

            RequestConfig(request, paginate).configure(asn_table)

            context["asn_range_table"] = asn_table

        return context


class BGPRoutingInstanceUIViewSet(NautobotUIViewSet):
    """UIViewset for BGPRoutingInstance model."""

    bulk_update_form_class = forms.BGPRoutingInstanceBulkEditForm
    filterset_class = filters.BGPRoutingInstanceFilterSet
    filterset_form_class = forms.BGPRoutingInstanceFilterForm
    form_class = forms.BGPRoutingInstanceForm
    lookup_field = "pk"
    queryset = models.BGPRoutingInstance.objects.all()
    serializer_class = serializers.BGPRoutingInstanceSerializer
    table_class = tables.BGPRoutingInstanceTable

    object_detail_content = ObjectDetailContent(
        extra_tabs=[
            extra_attributes_tab,
        ],
        panels=[
            ObjectFieldsPanel(
                weight=100,
                section=SectionChoices.LEFT_HALF,
                fields="__all__",
                exclude_fields=["extra_attributes"],
            ),
            ObjectsTablePanel(
                weight=100,
                section=SectionChoices.RIGHT_HALF,
                table_class=tables.PeerGroupTable,
                table_filter="routing_instance",
                show_table_config_button=False,
                paginate=False,
                include_columns=["name"],
                exclude_columns=set(tables.PeerGroupTable.Meta.default_columns).difference({"name"}),
            ),
            ObjectsTablePanel(
                weight=150,
                section=SectionChoices.RIGHT_HALF,
                table_class=tables.AddressFamilyTable,
                table_filter="routing_instance",
                show_table_config_button=False,
                paginate=False,
                include_columns=["address_family"],
                exclude_columns=set(tables.AddressFamilyTable.Meta.default_columns).difference({"address_family"}),
            ),
        ],
    )


class PeerGroupUIViewSet(NautobotUIViewSet):
    """UIViewset for PeerGroup model."""

    bulk_update_form_class = forms.PeerGroupBulkEditForm
    filterset_class = filters.PeerGroupFilterSet
    filterset_form_class = forms.PeerGroupFilterForm
    form_class = forms.PeerGroupForm
    lookup_field = "pk"
    queryset = models.PeerGroup.objects.all()
    serializer_class = serializers.PeerGroupSerializer
    table_class = tables.PeerGroupTable

    object_detail_content = ObjectDetailContent(
        extra_tabs=[
            extra_attributes_tab,
        ],
        panels=[
            BGPObjectsFieldPanel(
                weight=100,
                section=SectionChoices.LEFT_HALF,
                label="BGP Peer Group",
                fields=["name", "source_interface__parent", "routing_instance", "vrf"],
                key_transforms={"source_interface__parent": "Device"},
            ),
            BGPObjectsFieldPanel(
                weight=200,
                section=SectionChoices.LEFT_HALF,
                label="Peer Group Template",
                fields=["peergroup_template"],
            ),
            BGPObjectsFieldPanel(
                weight=300,
                section=SectionChoices.LEFT_HALF,
                label="Authentication",
                fields=["secret"],
            ),
            BGPObjectsFieldPanel(
                weight=400,
                section=SectionChoices.LEFT_HALF,
                label="Attributes",
                fields=["source_ip", "source_interface", "description", "enabled", "autonomous_system"],
            ),
            ObjectsTablePanel(
                weight=50,
                section=SectionChoices.RIGHT_HALF,
                table_class=tables.PeerEndpointTable,
                table_filter="peer_group",
                table_title="Peerings In This Group",
                show_table_config_button=False,
                paginate=False,
                include_columns=["peering"],
                exclude_columns=set(tables.PeerEndpointTable.Meta.default_columns).difference({"peering"}),
            ),
            ObjectsTablePanel(
                weight=100,
                section=SectionChoices.RIGHT_HALF,
                table_class=tables.PeerGroupAddressFamilyTable,
                table_filter="peer_group",
                show_table_config_button=False,
                paginate=False,
                include_columns=["peer_group_address_family"],
                exclude_columns=set(tables.PeerGroupAddressFamilyTable.Meta.default_columns).difference(
                    {"peer_group_address_family"}
                ),
            ),
        ],
    )


class PeerGroupTemplateUIViewSet(NautobotUIViewSet):
    """UIViewset for PeerGroupTemplate model."""

    bulk_update_form_class = forms.PeerGroupTemplateBulkEditForm
    filterset_class = filters.PeerGroupTemplateFilterSet
    filterset_form_class = forms.PeerGroupTemplateFilterForm
    form_class = forms.PeerGroupTemplateForm
    lookup_field = "pk"
    queryset = models.PeerGroupTemplate.objects.all()
    serializer_class = serializers.PeerGroupTemplateSerializer
    table_class = tables.PeerGroupTemplateTable

    object_detail_content = ObjectDetailContent(
        extra_tabs=[
            extra_attributes_tab,
        ],
        panels=[
            ObjectFieldsPanel(
                weight=100,
                section=SectionChoices.LEFT_HALF,
                label="BGP Peer Group Template",
                fields=["name"],
            ),
            ObjectFieldsPanel(
                weight=200,
                section=SectionChoices.LEFT_HALF,
                label="Authentication",
                fields=["secret"],
            ),
            ObjectFieldsPanel(
                weight=300,
                section=SectionChoices.LEFT_HALF,
                label="Attributes",
                fields=["description", "role", "enabled", "autonomous_system"],
            ),
        ],
    )


class PeerEndpointUIViewSet(NautobotUIViewSet):
    """UIViewset for PeerEndpoint model."""

    bulk_update_form_class = forms.PeerEndpointBulkEditForm
    filterset_class = filters.PeerEndpointFilterSet
    filterset_form_class = forms.PeerEndpointFilterForm
    form_class = forms.PeerEndpointForm
    lookup_field = "pk"
    queryset = models.PeerEndpoint.objects.all()
    serializer_class = serializers.PeerEndpointSerializer
    table_class = tables.PeerEndpointTable

    object_detail_content = ObjectDetailContent(
        extra_tabs=[
            extra_attributes_tab,
        ],
        panels=[
            BGPObjectsFieldPanel(
                weight=100,
                section=SectionChoices.LEFT_HALF,
                label="BGP Peer Endpoint",
                fields=["source_interface__parent", "routing_instance", "peer_group", "peering"],
                key_transforms={"source_interface__parent": "Device"},
            ),
            BGPObjectsFieldPanel(
                weight=200,
                section=SectionChoices.LEFT_HALF,
                label="Authentication",
                fields=["secret"],
            ),
            BGPObjectsFieldPanel(
                weight=300,
                section=SectionChoices.LEFT_HALF,
                label="Attributes",
                fields=["source_ip", "source_interface", "description", "enabled", "autonomous_system"],
            ),
            BGPObjectsFieldPanel(
                weight=100,
                section=SectionChoices.RIGHT_HALF,
                label="Remote Peer Information",
                fields=["peer"],
            ),
            ObjectsTablePanel(
                weight=200,
                section=SectionChoices.RIGHT_HALF,
                table_class=tables.PeerEndpointAddressFamilyTable,
                table_filter="peer_endpoint",
                show_table_config_button=False,
                paginate=False,
                include_columns=["peer_endpoint_address_family"],
                exclude_columns=set(tables.PeerEndpointAddressFamilyTable.Meta.default_columns).difference(
                    {"peer_endpoint_address_family"}
                ),
            ),
        ],
    )


class PeeringUIViewSet(  # pylint: disable=abstract-method
    ObjectDestroyViewMixin,
    ObjectBulkDestroyViewMixin,
    ObjectEditViewMixin,
    ObjectListViewMixin,
    ObjectDetailViewMixin,
    ObjectChangeLogViewMixin,
    ObjectNotesViewMixin,
):
    """UIViewset for Peering model."""

    action_buttons = (
        "add",
        "export",
    )
    filterset_class = filters.PeeringFilterSet
    filterset_form_class = forms.PeeringFilterForm
    form_class = forms.PeeringForm
    lookup_field = "pk"
    queryset = models.Peering.objects.all()
    serializer_class = serializers.PeeringSerializer
    table_class = tables.PeeringTable

    object_detail_content = ObjectDetailContent(
        extra_buttons=[
            DropdownButton(
                weight=100,
                color=ButtonColorChoices.YELLOW,
                label="Edit Peer Endpoint",
                icon=ButtonActionIconChoices.EDIT,
                required_permissions=["nautobot_bgp_models.change_peerendpoint"],
                children=(
                    Button(
                        weight=100,
                        link_name="plugins:nautobot_bgp_models:peerendpoint_edit",
                        label="Peer Endpoint A-side",
                        icon="mdi-alpha-a-box",
                        context_object_key="endpoint_a",
                    ),
                    Button(
                        weight=200,
                        link_name="plugins:nautobot_bgp_models:peerendpoint_edit",
                        label="Peer Endpoint Z-side",
                        icon="mdi-alpha-z-box",
                        context_object_key="endpoint_z",
                    ),
                ),
            ),
        ],
        panels=[
            BGPObjectsFieldPanel(
                weight=100,
                section=SectionChoices.LEFT_HALF,
                fields="__all__",
                exclude_fields=["extra_attributes"],
            ),
            BGPObjectsFieldPanel(
                weight=100,
                section=SectionChoices.RIGHT_HALF,
                label="BGP Peer Endpoint (A-side)",
                context_object_key="endpoint_a",
                fields="__all__",
                exclude_fields=["extra_attributes"],
            ),
            BGPObjectsFieldPanel(
                weight=150,
                section=SectionChoices.RIGHT_HALF,
                label="BGP Peer Endpoint (Z-side)",
                context_object_key="endpoint_z",
                fields="__all__",
                exclude_fields=["extra_attributes"],
            ),
        ],
    )

    def get_extra_context(self, request, instance=None):
        """Get extra context data."""
        context = super().get_extra_context(request, instance)

        if instance:
            context["endpoint_a"] = instance.endpoint_a
            context["endpoint_z"] = instance.endpoint_z

        return context


# TODO: This needs to be moved to the UIViewSet
class PeeringAddView(ObjectEditView):
    """Create view for a Peering."""

    queryset = models.Peering.objects.all()
    template_name = "nautobot_bgp_models/peering_add.html"

    def post(self, request, *args, **kwargs):
        """Post Method."""
        peering_form = forms.PeeringForm(request.POST, prefix="peering")
        peerendpoint_a_form = forms.PeerEndpointForm(request.POST, prefix="peerendpoint_a")
        peerendpoint_z_form = forms.PeerEndpointForm(request.POST, prefix="peerendpoint_z")

        try:
            if peering_form.is_valid() and peerendpoint_a_form.is_valid() and peerendpoint_z_form.is_valid():
                with transaction.atomic():
                    peering = peering_form.save()

                    endpoint_a = peerendpoint_a_form.save(commit=False)
                    endpoint_z = peerendpoint_z_form.save(commit=False)

                    for endpoint in [endpoint_a, endpoint_z]:
                        endpoint.peering = peering
                        endpoint.save()

                    peering.validate_peers()
                    peering.update_peers()

                return redirect(peering.get_absolute_url())
        except ValidationError as error:
            peering_form.add_error(field=None, error=error.message)

        return render(
            request,
            self.template_name,
            {
                "peering_form": peering_form,
                "peerendpoint_a_form": peerendpoint_a_form,
                "peerendpoint_z_form": peerendpoint_z_form,
                "forms": [peering_form, peerendpoint_a_form, peerendpoint_z_form],
            },
        )

    def get(self, request, *args, **kwargs):
        """Get method."""
        peering_form = forms.PeeringForm(prefix="peering")
        peerendpoint_a_form = forms.PeerEndpointForm(prefix="peerendpoint_a")
        peerendpoint_z_form = forms.PeerEndpointForm(prefix="peerendpoint_z")

        return render(
            request,
            self.template_name,
            {
                "peering_form": peering_form,
                "peerendpoint_a_form": peerendpoint_a_form,
                "peerendpoint_z_form": peerendpoint_z_form,
            },
        )


class AddressFamilyUIViewSet(NautobotUIViewSet):
    """UIViewset for AddressFamily model."""

    bulk_update_form_class = forms.AddressFamilyBulkEditForm
    filterset_class = filters.AddressFamilyFilterSet
    filterset_form_class = forms.AddressFamilyFilterForm
    form_class = forms.AddressFamilyForm
    lookup_field = "pk"
    queryset = models.AddressFamily.objects.all()
    serializer_class = serializers.AddressFamilySerializer
    table_class = tables.AddressFamilyTable

    object_detail_content = ObjectDetailContent(
        extra_tabs=[
            extra_attributes_tab,
        ],
        panels=[
            ObjectFieldsPanel(
                weight=100,
                section=SectionChoices.LEFT_HALF,
                label="BGP Address Family",
                fields=["routing_instance__device", "routing_instance"],
                key_transforms={"routing_instance__device": "Device"},
            ),
            ObjectFieldsPanel(
                weight=200,
                section=SectionChoices.LEFT_HALF,
                label="Attributes",
                fields=["afi_safi", "vrf"],
            ),
        ],
    )


class PeerGroupAddressFamilyUIViewSet(NautobotUIViewSet):
    """UIViewset for PeerGroupAddressFamily model."""

    bulk_update_form_class = forms.PeerGroupAddressFamilyBulkEditForm
    filterset_class = filters.PeerGroupAddressFamilyFilterSet
    filterset_form_class = forms.PeerGroupAddressFamilyFilterForm
    form_class = forms.PeerGroupAddressFamilyForm
    lookup_field = "pk"
    queryset = models.PeerGroupAddressFamily.objects.all()
    serializer_class = serializers.PeerGroupAddressFamilySerializer
    table_class = tables.PeerGroupAddressFamilyTable

    object_detail_content = ObjectDetailContent(
        extra_tabs=[
            extra_attributes_tab,
        ],
        panels=[
            BGPObjectsFieldPanel(
                weight=100,
                section=SectionChoices.LEFT_HALF,
                fields="__all__",
                exclude_fields=["extra_attributes"],
            ),
        ],
    )


class PeerEndpointAddressFamilyUIViewSet(NautobotUIViewSet):
    """UIViewset for PeerEndpointAddressFamily model."""

    bulk_update_form_class = forms.PeerEndpointAddressFamilyBulkEditForm
    filterset_class = filters.PeerEndpointAddressFamilyFilterSet
    filterset_form_class = forms.PeerEndpointAddressFamilyFilterForm
    form_class = forms.PeerEndpointAddressFamilyForm
    lookup_field = "pk"
    queryset = models.PeerEndpointAddressFamily.objects.all()
    serializer_class = serializers.PeerEndpointAddressFamilySerializer
    table_class = tables.PeerEndpointAddressFamilyTable

    object_detail_content = ObjectDetailContent(
        extra_tabs=[
            extra_attributes_tab,
        ],
        panels=[
            BGPObjectsFieldPanel(
                weight=100,
                section=SectionChoices.LEFT_HALF,
                fields=[
                    "peer_endpoint__source_interface__parent",
                    "peer_endpoint__routing_instance",
                    "peer_endpoint",
                    "afi_safi",
                    "import_policy",
                    "export_policy",
                    "multipath",
                ],
                key_transforms={
                    "peer_endpoint__source_interface__parent": "Device",
                    "peer_endpoint__routing_instance": "Routing Instance",
                },
            ),
        ],
    )
