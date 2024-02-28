"""Filter Extensions definitions for nautobot_bgp_models."""

from django import forms

from nautobot.apps.filters import FilterExtension, MultiValueCharFilter


class IPAddressFilterExtension(FilterExtension):
    """IP Address Filter Extension."""

    model = "ipam.ipaddress"

    filterset_fields = {
        "nautobot_bgp_models_ips_bgp_routing_instance": MultiValueCharFilter(
            field_name="interfaces__device__bgp_routing_instances__id",
            label="Routing Instance UUID",
        ),
    }

    filterform_fields = {
        "nautobot_bgp_models_ips_bgp_routing_instance": forms.CharField(required=False, label="Routing Instance UUID"),
    }


class InterfaceFilterExtension(FilterExtension):
    """Interface filter extension."""

    model = "dcim.interface"

    filterset_fields = {
        "nautobot_bgp_models_interfaces_bgp_routing_instance": MultiValueCharFilter(
            field_name="device__bgp_routing_instances__id",
            label="Routing Instance UUID",
        ),
    }

    filterform_fields = {
        "nautobot_bgp_models_interfaces_bgp_routing_instance": forms.CharField(
            required=False, label="Routing Instance UUID"
        ),
    }


filter_extensions = [InterfaceFilterExtension, IPAddressFilterExtension]
