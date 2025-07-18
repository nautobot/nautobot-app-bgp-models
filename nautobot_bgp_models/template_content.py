"""Extensions of baseline Nautobot views."""

from nautobot.extras.plugins import PluginTemplateExtension

from .models import AddressFamily, AutonomousSystem, BGPRoutingInstance, PeerEndpoint


class DevicePeerEndpoints(PluginTemplateExtension):  # pylint: disable=abstract-method
    """Add PeerEndpoints to the right side of the Device page."""

    model = "dcim.device"

    def right_page(self):
        """Add content to the right side of the Devices detail view."""
        endpoints = PeerEndpoint.objects.filter(
            routing_instance__device=self.context["object"],
        )
        if endpoints.exists():
            return self.render(
                "nautobot_bgp_models/inc/device_peer_endpoints.html",
                extra_context={"endpoints": endpoints},
            )
        else:
            return ""


class DeviceAddressFamilies(PluginTemplateExtension):  # pylint: disable=abstract-method
    """Add AddressFamilies to the right side of the Device page."""

    model = "dcim.device"

    def right_page(self):
        """Add content to the right side of the Device detail view."""
        address_families = AddressFamily.objects.filter(
            routing_instance__device=self.context["object"],
        )
        if address_families.exists():
            return self.render(
                "nautobot_bgp_models/inc/device_address_families.html",
                extra_context={"address_families": address_families},
            )
        else:
            return ""


class DeviceBgpRoutingInstances(PluginTemplateExtension):  # pylint: disable=abstract-method
    """Add BGPRoutingInstance to the right side of the Device page."""

    model = "dcim.device"

    def right_page(self):
        """Add content to the right side of the Device detail view."""
        bgp_routing_instances = BGPRoutingInstance.objects.filter(
            device=self.context["object"],
        )
        if bgp_routing_instances.exists():
            return self.render(
                "nautobot_bgp_models/inc/device_bgp_routing_instances.html",
                extra_context={"bgp_routing_instances": bgp_routing_instances},
            )
        else:
            return ""


class DeviceAutonomousSystems(PluginTemplateExtension):  # pylint: disable=abstract-method
    """Add AutonomousSystems to the right side of the Device page."""

    model = "dcim.device"

    def right_page(self):
        """Add content to the right side of the Device detail view."""
        autonomous_systems = (
            AutonomousSystem.objects.filter(
                bgproutinginstance__device=self.context["object"],
            )
            .distinct()
            .order_by("asn")
        )
        if autonomous_systems.exists():
            return self.render(
                "nautobot_bgp_models/inc/device_autonomous_systems.html",
                extra_context={"autonomous_systems": autonomous_systems},
            )
        else:
            return ""


template_extensions = [
    DeviceAutonomousSystems,
    DeviceBgpRoutingInstances,
    DeviceAddressFamilies,
    DevicePeerEndpoints,
]
