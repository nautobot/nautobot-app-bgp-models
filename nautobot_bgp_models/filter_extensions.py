"""Filter Extensions definitions for nautobot_bgp_models."""

from django import forms
from django.db.models import Q
from nautobot.apps.filters import FilterExtension, MultiValueCharFilter
from nautobot.dcim.constants import MODULE_RECURSION_DEPTH_LIMIT


def _q_routing_instance_ids_via_parent_device(value, prefix=""):
    """
    Build a Q that matches when the interface's parent device has any of the given routing instance IDs.

    Mirrors Interface.parent (device or module chain to device). Prefix is "" for Interface
    queryset, "interfaces__" for IPAddress queryset.
    """
    if not value:
        return Q(pk__in=[])
    if isinstance(value, str):
        value = [value]
    value = [str(v).strip() for v in value if v is not None and str(v).strip()]

    suffix = "bgp_routing_instances__id__in"
    query = Q(**{f"{prefix}device__{suffix}": value})
    recursion_depth = MODULE_RECURSION_DEPTH_LIMIT - 1
    for level in range(recursion_depth):
        recursive_part = "module__parent_module_bay__" + "parent_module__parent_module_bay__" * level
        query = query | Q(**{f"{prefix}{recursive_part}parent_device__{suffix}": value})
    return query


def _filter_ips_by_routing_instance(queryset, name, value):  # pylint: disable=unused-argument
    """Filter IPAddress queryset by routing instance UUID(s) via interface's parent device."""
    if not value:
        return queryset
    q = _q_routing_instance_ids_via_parent_device(value, "interfaces__")
    return queryset.filter(q).distinct()


def _filter_interfaces_by_routing_instance(queryset, name, value):  # pylint: disable=unused-argument
    """Filter Interface queryset by routing instance UUID(s) via parent device (device or module chain)."""
    if not value:
        return queryset
    q = _q_routing_instance_ids_via_parent_device(value)
    return queryset.filter(q)


class IPAddressFilterExtension(FilterExtension):
    """IP Address Filter Extension."""

    model = "ipam.ipaddress"

    filterset_fields = {
        "nautobot_bgp_models_ips_bgp_routing_instance": MultiValueCharFilter(
            method=_filter_ips_by_routing_instance,
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
            method=_filter_interfaces_by_routing_instance,
            label="Routing Instance UUID",
        ),
    }

    filterform_fields = {
        "nautobot_bgp_models_interfaces_bgp_routing_instance": forms.CharField(
            required=False, label="Routing Instance UUID"
        ),
    }


filter_extensions = [InterfaceFilterExtension, IPAddressFilterExtension]
