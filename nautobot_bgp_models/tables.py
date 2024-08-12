"""Table display definitions for nautobot_bgp_models."""

import django_tables2 as tables
from django_tables2.utils import A

from nautobot.apps.tables import (
    BaseTable,
    BooleanColumn,
    ButtonsColumn,
    ColoredLabelColumn,
    TagColumn,
    ToggleColumn,
    StatusTableMixin,
)

from . import models

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


class PeeringTable(StatusTableMixin, BaseTable):
    """Table representation of Peering records."""

    # TODO(mzb): Add columns: Device_A, Device_B, Provider_A, Provider_Z

    pk = ToggleColumn()
    peering = tables.LinkColumn(
        viewname="plugins:nautobot_bgp_models:peering",
        args=[A("pk")],
        text=str,
        orderable=False,
    )

    endpoint_a = tables.LinkColumn(
        verbose_name="Endpoint", text=lambda x: str(x.endpoint_a.local_ip) if x.endpoint_a else None, orderable=False
    )

    endpoint_z = tables.LinkColumn(
        verbose_name="Endpoint", text=lambda x: str(x.endpoint_z.local_ip) if x.endpoint_z else None, orderable=False
    )
    actions = ButtonsColumn(model=models.Peering)

    class Meta(BaseTable.Meta):
        model = models.Peering
        fields = (
            "pk",
            "peering",
            "endpoint_a",
            "endpoint_z",
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
