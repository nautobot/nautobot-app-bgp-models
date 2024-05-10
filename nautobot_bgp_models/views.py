"""View classes for nautobot_bgp_models."""

from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import View
from django_tables2 import RequestConfig

from nautobot.apps.views import NautobotUIViewSet
from nautobot.core.views import mixins
from nautobot.core.views import generic
from nautobot.extras.utils import get_base_template
from nautobot.core.views.paginator import EnhancedPaginator, get_paginate_count

from . import filters, forms, helpers, models, tables
from .api import serializers


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

    def get_extra_context(self, request, instance):  # pylint: disable=signature-differs
        """Return any additional context data for the template."""
        context = super().get_extra_context(request, instance)
        if self.action == "retrieve":
            context["object_fields"] = instance.get_fields(include_inherited=True)
        return context


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

    def get_extra_context(self, request, instance):  # pylint: disable=signature-differs
        """Return any additional context data for the template."""
        context = super().get_extra_context(request, instance)
        if self.action == "retrieve":
            context["object_fields"] = instance.get_fields(include_inherited=True)
        return context


class PeeringUIViewSet(  # pylint: disable=abstract-method
    mixins.ObjectDestroyViewMixin,
    mixins.ObjectBulkDestroyViewMixin,
    mixins.ObjectEditViewMixin,
    mixins.ObjectListViewMixin,
    mixins.ObjectDetailViewMixin,
    mixins.ObjectChangeLogViewMixin,
    mixins.ObjectNotesViewMixin,
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


# TODO: This needs to be moved to the UIViewSet
class PeeringAddView(generic.ObjectEditView):
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


class BgpExtraAttributesView(View):
    """BGP Extra Attributes View."""

    base_template = None

    def get(self, request, model, **kwargs):  # pylint: disable=missing-function-docstring
        """Getter."""
        # Handle QuerySet restriction of parent object if needed
        if hasattr(model.objects, "restrict"):
            obj = get_object_or_404(model.objects.restrict(request.user, "view"), **kwargs)
        else:
            obj = get_object_or_404(model, **kwargs)

        self.base_template = get_base_template(self.base_template, model)

        # Determine user's preferred output format
        if request.GET.get("format") in ["json", "yaml"]:
            _format = request.GET.get("format")
            if request.user.is_authenticated:
                request.user.set_config("nautobot_bgp_models.extraattributes.format", _format, commit=True)
        elif request.user.is_authenticated:
            _format = request.user.get_config("nautobot_bgp_models.extraattributes.format", "json")
        else:
            _format = "json"

        return render(
            request,
            "nautobot_bgp_models/extra_attributes.html",
            {
                "object": obj,
                "rendered_context": obj.get_extra_attributes(),
                "verbose_name": obj._meta.verbose_name,
                "verbose_name_plural": obj._meta.verbose_name_plural,
                # "table": objectchanges_table,
                "format": _format,
                "base_template": self.base_template,
                "active_tab": "extraattributes",
            },
        )
