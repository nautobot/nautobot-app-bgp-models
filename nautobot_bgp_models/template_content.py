# pylint: disable=abstract-method
"""Extensions of baseline Nautobot views."""

from nautobot.apps.ui import (
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
            table_class=tables.AutonomousSystemTable,
            table_filter="bgproutinginstance__device",
            add_button_route=None,
            show_table_config_button=False,
            paginate=False,
            include_columns=["asn"],
            exclude_columns=set(tables.AutonomousSystemTable.Meta.default_columns).difference({"asn"}),
        ),
        object_detail.ObjectsTablePanel(
            weight=200,
            section=SectionChoices.RIGHT_HALF,
            table_class=tables.BGPRoutingInstanceTable,
            table_filter="device",
            add_button_route=None,
            show_table_config_button=False,
            paginate=False,
            include_columns=["routing_instance"],
            exclude_columns=set(tables.BGPRoutingInstanceTable.Meta.default_columns).difference({"routing_instance"}),
        ),
        object_detail.ObjectsTablePanel(
            weight=300,
            section=SectionChoices.RIGHT_HALF,
            table_class=tables.AddressFamilyTable,
            table_filter="routing_instance__device",
            add_button_route=None,
            show_table_config_button=False,
            paginate=False,
            include_columns=["routing_instance", "address_family"],
            exclude_columns=set(tables.AddressFamilyTable.Meta.default_columns).difference(
                {"routing_instance", "address_family"}
            ),
        ),
        object_detail.ObjectsTablePanel(
            weight=400,
            section=SectionChoices.RIGHT_HALF,
            table_class=tables.PeerEndpointTable,
            table_filter="routing_instance__device",
            add_button_route=None,
            show_table_config_button=False,
            paginate=False,
            table_title="BGP Peerings",
            include_columns=["peering"],
            exclude_columns=set(tables.PeerEndpointTable.Meta.default_columns).difference({"peering"}),
        ),
    )


template_extensions = [
    DeviceContent,
]
