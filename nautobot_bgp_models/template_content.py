# pylint: disable=abstract-method
"""Extensions of baseline Nautobot views."""

from nautobot.apps.ui import (
    ObjectTextPanel,
    SectionChoices,
    TemplateExtension,
)
from nautobot.core.ui import object_detail

from nautobot_bgp_models import tables

extra_attributes_tab = object_detail.Tab(
    weight=100,
    tab_id="Extra Attributes",
    label="Extra Attributes",
    panels=[
        object_detail.ObjectTextPanel(
            weight=100,
            section=SectionChoices.LEFT_HALF,
            label="Rendered BGP Extra Attributes (includes inherited)",
            object_field="extra_attributes",
            render_as=ObjectTextPanel.RenderOptions.JSON,
        ),
        object_detail.ObjectTextPanel(
            weight=100,
            section=SectionChoices.RIGHT_HALF,
            label="BGP object's extra attributes (The local BGP object's extra attribute overwrite all inherited attributes.)",
            object_field="extra_attributes_inherited",
            render_as=ObjectTextPanel.RenderOptions.JSON,
        ),
    ],
)


class AddressFamilyContent(TemplateExtension):
    """Template extension for Address Family content."""

    model = "nautobot_bgp_models.addressfamily"
    object_detail_tabs = (extra_attributes_tab,)


class BGPRoutingInstanceContent(TemplateExtension):
    """Template extension for BGP Routing Instance content."""

    model = "nautobot_bgp_models.bgproutinginstance"
    object_detail_tabs = (extra_attributes_tab,)


class PeerEndpointContent(TemplateExtension):
    """Template extension for Peer Endpoint content."""

    model = "nautobot_bgp_models.peerendpoint"
    object_detail_tabs = (extra_attributes_tab,)


class PeerGroupContent(TemplateExtension):
    """Template extension for Peer Group content."""

    model = "nautobot_bgp_models.peergroup"
    object_detail_tabs = (extra_attributes_tab,)


class PeerGroupTemplateContent(TemplateExtension):
    """Template extension for Peer Group Template content."""

    model = "nautobot_bgp_models.peergrouptemplate"
    object_detail_tabs = (extra_attributes_tab,)


class PeerGroupAddressFamilyContent(TemplateExtension):
    """Template extension for Peer Group Address Family content."""

    model = "nautobot_bgp_models.peergroupaddressfamily"
    object_detail_tabs = (extra_attributes_tab,)


class PeerEndpointAddressFamilyContent(TemplateExtension):
    """Template extension for Peer Endpoint Address Family content."""

    model = "nautobot_bgp_models.peerendpointaddressfamily"
    object_detail_tabs = (extra_attributes_tab,)


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
    AddressFamilyContent,
    BGPRoutingInstanceContent,
    PeerEndpointContent,
    PeerGroupContent,
    PeerGroupTemplateContent,
    PeerGroupAddressFamilyContent,
    PeerEndpointAddressFamilyContent,
]
