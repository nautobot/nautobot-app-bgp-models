"""Extensions of baseline Nautobot views."""
from django.contrib.contenttypes.models import ContentType

from nautobot.extras.plugins import PluginTemplateExtension

from .models import AddressFamily, PeerEndpoint


class DevicePeerEndpoints(PluginTemplateExtension):  # pylint: disable=abstract-method
    """Add PeerEndpoints to the right side of the Device page."""

    model = "dcim.device"

    def right_page(self):
        """Add content to the right side of the Devices detail view."""
        # TODO: would be more efficient if we could do PeerEndpoint.objects.filter(device=...)
        endpoints = [
            endpoint for endpoint in PeerEndpoint.objects.all() if endpoint.get_device() == self.context["object"]
        ]
        return self.render(
            "nautobot_bgp_models/inc/device_peer_endpoints.html",
            extra_context={"endpoints": endpoints},
        )


class DeviceAddressFamilies(PluginTemplateExtension):  # pylint: disable=abstract-method
    """Add AddressFamilies to the right side of the Device page."""

    model = "dcim.device"

    def right_page(self):
        """Add content to the right side of the Device detail view."""
        address_families = AddressFamily.objects.filter(
            device_content_type=ContentType.objects.get_for_model(self.context["object"]),
            device_object_id=self.context["object"].pk,
        )
        return self.render(
            "nautobot_bgp_models/inc/device_address_families.html",
            extra_context={"address_families": address_families},
        )


template_extensions = [
    # DeviceAddressFamilies,  # Disabled for now due to potential performance concerns
    # DevicePeerEndpoints,  # Disabled for now; performs very poorly when there are many PeerEndpoint records.
]
