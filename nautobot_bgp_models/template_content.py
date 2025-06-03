"""Extensions of baseline Nautobot views."""

from django_tables2 import RequestConfig
from nautobot.extras.plugins import PluginTemplateExtension

from .models import AddressFamily, BGPRoutingInstance, PeerEndpoint
from .tables import DevicePeerEndpointsTable


class DevicePeerEndpoints(PluginTemplateExtension):  # pylint: disable=abstract-method
    """Add PeerEndpoints to the right side of the Device page."""

    model = "dcim.device"

    def right_page(self):
        """Add content to the right side of the Devices detail view."""
        endpoints = PeerEndpoint.objects.filter(
            routing_instance__device=self.context["object"],
        )

        table = DevicePeerEndpointsTable(endpoints)
        RequestConfig(self.context["request"], paginate={"per_page": 25}).configure(table)

        return self.render(
            "nautobot_bgp_models/inc/device_peer_endpoints_table.html",
            extra_context={"table": table},
        )


class DeviceAddressFamilies(PluginTemplateExtension):  # pylint: disable=abstract-method
    """Add AddressFamilies to the right side of the Device page."""

    model = "dcim.device"

    def right_page(self):
        """Add content to the right side of the Device detail view."""
        address_families = AddressFamily.objects.filter(
            routing_instance__device=self.context["object"],
        )
        return self.render(
            "nautobot_bgp_models/inc/device_address_families.html",
            extra_context={"address_families": address_families},
        )


class DeviceBgpRoutingInstances(PluginTemplateExtension):  # pylint: disable=abstract-method
    """Add BGPRoutingInstance to the right side of the Device page."""

    model = "dcim.device"

    def right_page(self):
        """Add content to the right side of the Device detail view."""
        bgp_routing_instances = BGPRoutingInstance.objects.filter(
            device=self.context["object"],
        )
        return self.render(
            "nautobot_bgp_models/inc/device_bgp_routing_instances.html",
            extra_context={"bgp_routing_instances": bgp_routing_instances},
        )


template_extensions = [
    DeviceBgpRoutingInstances,
    DeviceAddressFamilies,
    DevicePeerEndpoints,
]
