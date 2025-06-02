"""Table display definitions for nautobot_bgp_models."""

import django_tables2 as tables
from django_tables2.utils import A
from nautobot.apps.tables import (
    BaseTable,
    BooleanColumn,
    ButtonsColumn,
    ColoredLabelColumn,
    StatusTableMixin,
    TagColumn,
    ToggleColumn,
)

from . import models
from .table_columns import (
    AASNColumn,
    ADeviceColumn,
    AEndpointIPColumn,
    AProviderColumn,
    ZASNColumn,
    ZDeviceColumn,
    ZEndpointIPColumn,
    ZProviderColumn,
)

ASN_LINK = """
{% if record.present_in_database %}
<a href="{{ record.get_absolute_url }}">{{ record.asn }}</a>
{% elif perms.nautobot_bgp_models.autonomoussystem_add %}
<a href="\
{% url 'plugins:nautobot_bgp_models:autonomoussystem_add' %}\
?asn={{ record.asn }}\
" class="btn btn-xs btn-success">{{ record.available }} ASN{{ record.available|pluralize }} available</a>\
{% else %}
{{ record.available }} ASN{{ record.available|pluralize }} available
{% endif %}
"""


def extract_endpoint_from_peering(peering_str, side='a'):
    """Extract device endpoint information from peering string.
    
    Args:
        peering_str: String like "leaf9-cp1-smn1-hfa01 7.240.169.157/32 (AS 4266004237) ↔︎ core1-cp1-smn1-hfa01 7.240.169.0/32 (AS 4266004040)"
        side: 'a' for left side (before ↔︎), 'z' for right side (after ↔︎)
    
    Returns:
        Full endpoint string (device name + IP + ASN) or the original string if parsing fails
    """
    if not peering_str or '↔︎' not in str(peering_str):
        return str(peering_str)
    
    try:
        parts = str(peering_str).split(' ↔︎ ')
        if len(parts) != 2:
            return str(peering_str)
        
        endpoint_str = parts[0].strip() if side == 'a' else parts[1].strip()
        
        # Return the full endpoint string (device name + IP + ASN)
        return endpoint_str
        
    except Exception:
        return str(peering_str)


class AutonomousSystemTable(StatusTableMixin, BaseTable):
    """Table representation of AutonomousSystem records."""

    pk = ToggleColumn()
    asn = tables.TemplateColumn(template_code=ASN_LINK, verbose_name="ASN")
    provider = tables.LinkColumn()
    tags = TagColumn(url_name="plugins:nautobot_bgp_models:autonomoussystem_list")
    actions = ButtonsColumn(model=models.AutonomousSystem)
    asn_asdot = tables.Column(accessor=A("asn_asdot"), linkify=True, order_by=A("asn"), verbose_name="ASN ASDOT")

    class Meta(BaseTable.Meta):
        model = models.AutonomousSystem
        fields = ("pk", "asn", "asn_asdot", "status", "provider", "description", "tags")
        default_columns = ("pk", "asn", "status", "provider", "description", "tags")


class AutonomousSystemRangeTable(StatusTableMixin, BaseTable):
    """Table representation of AutonomousSystem records."""

    pk = ToggleColumn()
    name = tables.LinkColumn()
    asn_min = tables.LinkColumn()
    asn_max = tables.LinkColumn()
    tenant = tables.LinkColumn()
    tags = TagColumn(url_name="plugins:nautobot_bgp_models:autonomoussystemrange_list")
    actions = ButtonsColumn(model=models.AutonomousSystemRange)

    class Meta(BaseTable.Meta):
        model = models.AutonomousSystemRange
        fields = ("pk", "name", "asn_min", "asn_max", "tenant", "description", "tags")


class BGPRoutingInstanceTable(StatusTableMixin, BaseTable):
    """Table representation of BGPRoutingInstance records."""

    pk = ToggleColumn()
    routing_instance = tables.LinkColumn(
        viewname="plugins:nautobot_bgp_models:bgproutinginstance",
        args=[A("pk")],
        text=str,
    )
    device = tables.LinkColumn()
    autonomous_system = tables.LinkColumn()
    router_id = tables.LinkColumn()
    tags = TagColumn(url_name="plugins:nautobot_bgp_models:bgproutinginstance_list")
    actions = ButtonsColumn(model=models.BGPRoutingInstance)

    class Meta(BaseTable.Meta):
        model = models.BGPRoutingInstance
        fields = ("pk", "routing_instance", "device", "autonomous_system", "router_id", "tags")
        default_columns = (
            "pk",
            "routing_instance",
            "device",
            "autonomous_system",
            "router_id",
            "actions",
            "status",
        )


class PeerGroupTable(BaseTable):
    """Table representation of PeerGroup records."""

    pk = ToggleColumn()
    name = tables.LinkColumn()
    peergroup_template = tables.LinkColumn()
    routing_instance = tables.LinkColumn()
    vrf = tables.LinkColumn()
    enabled = BooleanColumn()
    role = ColoredLabelColumn()
    autonomous_system = tables.LinkColumn()
    secret = tables.LinkColumn()
    source_ip = tables.LinkColumn()
    source_interface = tables.LinkColumn()
    tags = TagColumn(url_name="plugins:nautobot_bgp_models:peergroup_list")

    actions = ButtonsColumn(model=models.PeerGroup)

    class Meta(BaseTable.Meta):
        model = models.PeerGroup
        fields = (
            "pk",
            "name",
            "peergroup_template",
            "routing_instance",
            "vrf",
            "enabled",
            "role",
            "autonomous_system",
            "source_ip",
            "source_interface",
            "secret",
            "tags",
        )
        default_columns = (
            "pk",
            "name",
            "peergroup_template",
            "routing_instance",
            "vrf",
            "enabled",
            "role",
            "autonomous_system",
            "actions",
        )


class PeerGroupTemplateTable(BaseTable):
    """Table representation of PeerGroup records."""

    pk = ToggleColumn()
    name = tables.LinkColumn()
    enabled = BooleanColumn()
    role = ColoredLabelColumn()
    autonomous_system = tables.LinkColumn()
    secret = tables.LinkColumn()
    actions = ButtonsColumn(model=models.PeerGroupTemplate)

    class Meta(BaseTable.Meta):
        model = models.PeerGroupTemplate
        fields = (
            "pk",
            "name",
            "enabled",
            "role",
            "autonomous_system",
            "secret",
        )
        default_columns = (
            "pk",
            "name",
            "enabled",
            "role",
            "autonomous_system",
            "secret",
            # "actions",
        )


class PeerEndpointTable(BaseTable):
    """Table representation of PeerEndpoint records."""

    pk = ToggleColumn()
    id = tables.LinkColumn()
    routing_instance = tables.LinkColumn()
    role = ColoredLabelColumn()
    source_ip = tables.LinkColumn()
    source_interface = tables.LinkColumn()
    autonomous_system = tables.LinkColumn()
    remote_autonomous_system = tables.LinkColumn()
    peer = tables.LinkColumn()
    peering = tables.LinkColumn()
    vrf = tables.LinkColumn()
    peer_group = tables.LinkColumn()
    tags = TagColumn(url_name="plugins:nautobot_bgp_models:peerendpoint_list")
    # actions = ButtonsColumn(model=models.PeerEndpoint)

    class Meta(BaseTable.Meta):
        model = models.PeerEndpoint
        fields = (
            "pk",
            "id",
            "routing_instance",
            "role",
            "source_ip",
            "source_interface",
            "autonomous_system",
            "remote_autonomous_system",
            "peer",
            "peering",
            "vrf",
            "peer_group",
            "tags",
        )
        default_columns = (
            "pk",
            "id",
            "routing_instance",
            "role",
            "source_ip",
            "source_interface",
            "autonomous_system",
            "remote_autonomous_system",
            "peer",
            "peering",
            "vrf",
            "peer_group",
        )


class DevicePeerEndpointTable(BaseTable):
    """Simplified table representation of PeerEndpoint records for device detail view."""

    peer_endpoint_a = tables.LinkColumn(
        accessor="id",
        viewname="plugins:nautobot_bgp_models:peerendpoint",
        args=[A("pk")],  # Link to the current record (this endpoint)
        verbose_name="Peer Endpoint A",
        text=lambda record: str(record),
    )
    
    peer_endpoint_z = tables.LinkColumn(
        accessor="peer",
        viewname="plugins:nautobot_bgp_models:peerendpoint", 
        args=[A("peer.pk")],  # Link to the peer record (the other endpoint)
        verbose_name="Peer Endpoint Z",
        text=lambda record: str(record.peer) if record.peer else "No peer",
    )

    class Meta(BaseTable.Meta):
        model = models.PeerEndpoint
        fields = (
            "peer_endpoint_a",
            "peer_endpoint_z", 
        )
        default_columns = (
            "peer_endpoint_a",
            "peer_endpoint_z",
        )
        orderable = False
        empty_text = "No BGP peer endpoints found for this device."


class PeeringTable(StatusTableMixin, BaseTable):
    """Table representation of Peering records."""

    pk = ToggleColumn()
    peering = tables.LinkColumn(
        viewname="plugins:nautobot_bgp_models:peering",
        args=[A("pk")],
        text=str,
        orderable=False,
    )
    a_side_device = ADeviceColumn(verbose_name="A Side Device")
    a_endpoint = AEndpointIPColumn(verbose_name="A Endpoint")
    a_side_asn = AASNColumn(verbose_name="A Side ASN")
    provider_a = AProviderColumn(verbose_name="Provider A")
    z_side_device = ZDeviceColumn(verbose_name="Z Side Device")
    z_endpoint = ZEndpointIPColumn(verbose_name="Z Endpoint")
    z_side_asn = ZASNColumn(verbose_name="Z Side ASN")
    provider_z = ZProviderColumn(verbose_name="Provider Z")

    actions = ButtonsColumn(model=models.Peering)

    class Meta(BaseTable.Meta):
        model = models.Peering
        fields = (
            "pk",
            "peering",
            "a_side_device",
            "a_endpoint",
            "a_side_asn",
            "provider_a",
            "z_side_device",
            "z_endpoint",
            "z_side_asn",
            "provider_z",
            "status",
        )


class AddressFamilyTable(BaseTable):
    """Table representation of AddressFamily records."""

    pk = ToggleColumn()
    address_family = tables.LinkColumn(
        viewname="plugins:nautobot_bgp_models:addressfamily",
        args=[A("pk")],
        text=str,
    )
    routing_instance = tables.LinkColumn()
    afi_safi = tables.Column()
    vrf = tables.LinkColumn()
    actions = ButtonsColumn(model=models.AddressFamily)

    class Meta(BaseTable.Meta):
        model = models.AddressFamily
        fields = (
            "pk",
            "address_family",
            "routing_instance",
            "afi_safi",
            "vrf",
        )
        default_columns = (
            "pk",
            "address_family",
            "routing_instance",
            "afi_safi",
            "vrf",
            "actions",
        )


class PeerGroupAddressFamilyTable(BaseTable):
    """Table representation of PeerGroupAddressFamily records."""

    pk = ToggleColumn()
    peer_group_address_family = tables.LinkColumn(
        viewname="plugins:nautobot_bgp_models:peergroupaddressfamily",
        args=[A("pk")],
        text=str,
    )
    peer_group = tables.LinkColumn()
    afi_safi = tables.Column()
    actions = ButtonsColumn(model=models.PeerGroupAddressFamily)

    class Meta(BaseTable.Meta):
        model = models.PeerGroupAddressFamily
        fields = (
            "pk",
            "peer_group_address_family",
            "peer_group",
            "afi_safi",
            "import_policy",
            "export_policy",
            "multipath",
        )
        default_columns = (
            "pk",
            "peer_group_address_family",
            "peer_group",
            "afi_safi",
            "import_policy",
            "export_policy",
            "multipath",
            "actions",
        )


class PeerEndpointAddressFamilyTable(BaseTable):
    """Table representation of PeerEndpointAddressFamily records."""

    pk = ToggleColumn()
    peer_endpoint_address_family = tables.LinkColumn(
        viewname="plugins:nautobot_bgp_models:peerendpointaddressfamily",
        args=[A("pk")],
        text=str,
    )
    peer_endpoint = tables.LinkColumn()
    afi_safi = tables.Column()
    actions = ButtonsColumn(model=models.PeerEndpointAddressFamily)

    class Meta(BaseTable.Meta):
        model = models.PeerEndpointAddressFamily
        fields = (
            "pk",
            "peer_endpoint_address_family",
            "peer_endpoint",
            "afi_safi",
            "import_policy",
            "export_policy",
            "multipath",
        )
        default_columns = (
            "pk",
            "peer_endpoint_address_family",
            "peer_endpoint",
            "afi_safi",
            "import_policy",
            "export_policy",
            "multipath",
            "actions",
        )
