"""Custom table columns for nautobot_bgp_models."""

import django_tables2 as tables
from django.db import models
from django.urls import reverse
from django.utils.html import format_html

from nautobot_bgp_models.models import PeerEndpoint


class BaseEndpointColumn(tables.Column):
    """Base class for endpoint-related columns."""

    def __init__(self, *args, **kwargs):
        """Initialize BaseEndpointColumn."""
        kwargs.setdefault("empty_values", ())
        super().__init__(*args, **kwargs)


class ADeviceColumn(BaseEndpointColumn):
    """Column for A Side Device."""

    def render(self, record):  # pylint: disable=arguments-renamed
        """Render A Side Device."""
        if record.endpoint_a and record.endpoint_a.routing_instance and record.endpoint_a.routing_instance.device:
            device = record.endpoint_a.routing_instance.device
            return format_html('<a href="{}">{}</a>', device.get_absolute_url(), device)
        return None

    def order(self, queryset, is_descending):
        """Custom ordering for A Side Device."""
        # Use a subquery to get specifically the first endpoint's device name
        first_endpoint_device = (
            PeerEndpoint.objects.filter(peering=models.OuterRef("pk"))
            .order_by("pk")
            .values("routing_instance__device__name")[:1]
        )

        queryset = queryset.annotate(a_device_name=models.Subquery(first_endpoint_device)).order_by(
            ("-" if is_descending else "") + "a_device_name"
        )

        return queryset, True


class ZDeviceColumn(BaseEndpointColumn):
    """Column for Z Side Device."""

    def render(self, record):  # pylint: disable=arguments-renamed
        """Render Z Side Device."""
        if record.endpoint_z and record.endpoint_z.routing_instance and record.endpoint_z.routing_instance.device:
            device = record.endpoint_z.routing_instance.device
            return format_html('<a href="{}">{}</a>', device.get_absolute_url(), device)
        return None

    def order(self, queryset, is_descending):
        """Custom ordering for Z Side Device."""
        # Use a subquery to get specifically the second endpoint's device name
        second_endpoint_device = (
            PeerEndpoint.objects.filter(peering=models.OuterRef("pk"))
            .order_by("pk")
            .values("routing_instance__device__name")[1:2]
        )

        queryset = queryset.annotate(z_device_name=models.Subquery(second_endpoint_device)).order_by(
            ("-" if is_descending else "") + "z_device_name"
        )

        return queryset, True


class AEndpointIPColumn(BaseEndpointColumn):
    """Column for A Endpoint IP."""

    def render(self, record):  # pylint: disable=arguments-renamed
        """Render A Endpoint IP."""
        if record.endpoint_a:
            if record.endpoint_a.local_ip:
                url = reverse("plugins:nautobot_bgp_models:peerendpoint", args=[record.endpoint_a.pk])
                return format_html('<a href="{}">{}</a>', url, record.endpoint_a.local_ip)
        return None

    def order(self, queryset, is_descending):
        """Custom ordering for A Endpoint IP."""
        first_endpoint_interface_ip = (
            PeerEndpoint.objects.filter(peering=models.OuterRef("pk"))
            .order_by("pk")
            .values(
                "source_interface__ip_addresses__mask_length",
                "source_interface__ip_addresses__ip_version",
                "source_interface__ip_addresses__host",
            )[:1]
        )

        queryset = queryset.annotate(
            a_endpoint_mask=models.Subquery(
                first_endpoint_interface_ip.values("source_interface__ip_addresses__mask_length")
            ),
            a_endpoint_ip_version=models.Subquery(
                first_endpoint_interface_ip.values("source_interface__ip_addresses__ip_version")
            ),
            a_endpoint_host=models.Subquery(first_endpoint_interface_ip.values("source_interface__ip_addresses__host")),
        )

        if is_descending:
            order_fields = ["a_endpoint_mask", "-a_endpoint_ip_version", "-a_endpoint_host"]
        else:
            order_fields = ["-a_endpoint_mask", "a_endpoint_ip_version", "a_endpoint_host"]

        return queryset.order_by(*order_fields), True


class ZEndpointIPColumn(BaseEndpointColumn):
    """Column for Z Endpoint IP."""

    def render(self, record):  # pylint: disable=arguments-renamed
        """Render Z Endpoint IP."""
        if record.endpoint_z and record.endpoint_z.local_ip:
            url = reverse("plugins:nautobot_bgp_models:peerendpoint", args=[record.endpoint_z.pk])
            return format_html('<a href="{}">{}</a>', url, record.endpoint_z.local_ip)
        return None

    def order(self, queryset, is_descending):
        """Custom ordering for Z Endpoint IP."""
        second_endpoint_interface_ip = (
            PeerEndpoint.objects.filter(peering=models.OuterRef("pk"))
            .order_by("pk")
            .values(
                "source_interface__ip_addresses__mask_length",
                "source_interface__ip_addresses__ip_version",
                "source_interface__ip_addresses__host",
            )[1:2]
        )

        queryset = queryset.annotate(
            z_endpoint_mask=models.Subquery(
                second_endpoint_interface_ip.values("source_interface__ip_addresses__mask_length")
            ),
            z_endpoint_ip_version=models.Subquery(
                second_endpoint_interface_ip.values("source_interface__ip_addresses__ip_version")
            ),
            z_endpoint_host=models.Subquery(
                second_endpoint_interface_ip.values("source_interface__ip_addresses__host")
            ),
        )

        if is_descending:
            order_fields = ["z_endpoint_mask", "-z_endpoint_ip_version", "-z_endpoint_host"]
        else:
            order_fields = ["-z_endpoint_mask", "z_endpoint_ip_version", "z_endpoint_host"]

        return queryset.order_by(*order_fields), True


class AASNColumn(BaseEndpointColumn):
    """Column for A Side ASN."""

    def render(self, record):  # pylint: disable=arguments-renamed
        """Render A Side ASN using inherited autonomous system."""
        if record.endpoint_a:
            asn, _, _ = record.endpoint_a.get_inherited_field("autonomous_system")
            if asn:
                url = reverse("plugins:nautobot_bgp_models:autonomoussystem", args=[asn.pk])
                return format_html('<a href="{}">{}</a>', url, asn.asn)
        return None

    def order(self, queryset, is_descending):
        """Custom ordering for A Side ASN."""
        first_endpoint_asn = (
            PeerEndpoint.objects.filter(peering=models.OuterRef("pk"))
            .order_by("pk")
            .values("routing_instance__autonomous_system__asn")[:1]
        )

        queryset = queryset.annotate(a_side_asn_value=models.Subquery(first_endpoint_asn))

        order_field = "-a_side_asn_value" if is_descending else "a_side_asn_value"
        return queryset.order_by(order_field), True


class ZASNColumn(BaseEndpointColumn):
    """Column for Z Side ASN."""

    def render(self, record):  # pylint: disable=arguments-renamed
        """Render Z Side ASN using inherited autonomous system."""
        if record.endpoint_z:
            asn, _, _ = record.endpoint_z.get_inherited_field("autonomous_system")
            if asn:
                url = reverse("plugins:nautobot_bgp_models:autonomoussystem", args=[asn.pk])
                return format_html('<a href="{}">{}</a>', url, asn.asn)
        return None

    def order(self, queryset, is_descending):
        """Custom ordering for Z Side ASN."""
        second_endpoint_asn = (
            PeerEndpoint.objects.filter(peering=models.OuterRef("pk"))
            .order_by("pk")
            .values("routing_instance__autonomous_system__asn")[1:2]
        )

        queryset = queryset.annotate(z_side_asn_value=models.Subquery(second_endpoint_asn))

        order_field = "-z_side_asn_value" if is_descending else "z_side_asn_value"
        return queryset.order_by(order_field), True


class AProviderColumn(BaseEndpointColumn):
    """Column for A Side Provider."""

    def render(self, record):  # pylint: disable=arguments-renamed
        """Render Provider A using inherited autonomous system."""
        if record.endpoint_a:
            asn, _, _ = record.endpoint_a.get_inherited_field("autonomous_system")
            if asn and asn.provider:
                url = reverse("circuits:provider", args=[asn.provider.pk])
                return format_html('<a href="{}">{}</a>', url, asn.provider)
        return None

    def order(self, queryset, is_descending):
        """Custom ordering for A Side Provider."""
        first_endpoint_provider = (
            PeerEndpoint.objects.filter(peering=models.OuterRef("pk"))
            .order_by("pk")
            .values("routing_instance__autonomous_system__provider__name")[:1]
        )

        queryset = queryset.annotate(a_side_provider_name=models.Subquery(first_endpoint_provider))

        order_field = "-a_side_provider_name" if is_descending else "a_side_provider_name"
        return queryset.order_by(order_field), True


class ZProviderColumn(BaseEndpointColumn):
    """Column for Z Side Provider."""

    def render(self, record):  # pylint: disable=arguments-renamed
        """Render Provider Z using inherited autonomous system."""
        if record.endpoint_z:
            asn, _, _ = record.endpoint_z.get_inherited_field("autonomous_system")
            if asn and asn.provider:
                url = reverse("circuits:provider", args=[asn.provider.pk])
                return format_html('<a href="{}">{}</a>', url, asn.provider)
        return None

    def order(self, queryset, is_descending):
        """Custom ordering for Z Side Provider."""
        second_endpoint_provider = (
            PeerEndpoint.objects.filter(peering=models.OuterRef("pk"))
            .order_by("pk")
            .values("routing_instance__autonomous_system__provider__name")[1:2]
        )

        queryset = queryset.annotate(z_side_provider_name=models.Subquery(second_endpoint_provider))

        order_field = "-z_side_provider_name" if is_descending else "z_side_provider_name"
        return queryset.order_by(order_field), True
