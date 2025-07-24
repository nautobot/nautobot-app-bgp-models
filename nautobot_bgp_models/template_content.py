# pylint: disable=abstract-method
"""Extensions of baseline Nautobot views."""

from nautobot.apps.ui import (
    ObjectTextPanel,
    SectionChoices,
    TemplateExtension,
)
from nautobot.core.ui import object_detail

from nautobot_bgp_models import tables



class DeviceContent(TemplateExtension):
    """Template extension for Device content."""

    model = "dcim.device"

    object_detail_panels = (
        object_detail.ObjectsTablePanel(
            weight=100,
            section=SectionChoices.RIGHT_HALF,
            table_class=tables.BGPRoutingInstanceTable,
            table_filter="device",
        ),
        object_detail.ObjectsTablePanel(
            weight=200,
            section=SectionChoices.RIGHT_HALF,
            table_class=tables.PeerEndpointTable,
            table_filter="routing_instance__device",
        ),
        object_detail.ObjectsTablePanel(
            weight=300,
            section=SectionChoices.RIGHT_HALF,
            table_class=tables.AddressFamilyTable,
            table_filter="routing_instance__device",
        ),
    )


template_extensions = [
    DeviceContent,
]
