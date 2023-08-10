"""Table display definitions for nautobot_bgp_models."""

import django_tables2 as tables
from django_tables2.utils import A

from nautobot.extras.tables import StatusTableMixin
from nautobot.utilities.tables import (
    BaseTable,
    BooleanColumn,
    ButtonsColumn,
    ColorColumn,
    ColoredLabelColumn,
    TagColumn,
    ToggleColumn,
)

from . import models


class AutonomousSystemTable(StatusTableMixin, BaseTable):
    """Table representation of AutonomousSystem records."""

    pk = ToggleColumn()
    asn = tables.LinkColumn()
    provider = tables.LinkColumn()
    tags = TagColumn(url_name="plugins:nautobot_bgp_models:autonomoussystem_list")
    actions = ButtonsColumn(model=models.AutonomousSystem)

    class Meta(BaseTable.Meta):
        model = models.AutonomousSystem
        fields = ("pk", "asn", "status", "provider", "description", "tags")


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
    tags = TagColumn(url_name="plugins:nautobot_bgp_models:BGPRoutingInstance_list")
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


class PeeringRoleTable(BaseTable):
    """Table representation of PeeringRole records."""

    pk = ToggleColumn()
    name = tables.LinkColumn()
    color = ColorColumn()
    actions = ButtonsColumn(model=models.PeeringRole, pk_field="slug")

    class Meta(BaseTable.Meta):
        model = models.PeeringRole
        fields = (
            "pk",
            "name",
            "slug",
            "color",
            "description",
        )


class PeerGroupTable(BaseTable):
    """Table representation of PeerGroup records."""

    pk = ToggleColumn()
    name = tables.LinkColumn()
    peergroup_template = tables.LinkColumn()
    routing_instance = tables.LinkColumn()
    enabled = BooleanColumn()
    role = ColoredLabelColumn()
    autonomous_system = tables.LinkColumn()
    secret = tables.LinkColumn()
    source_ip = tables.LinkColumn()
    source_interface = tables.LinkColumn()

    actions = ButtonsColumn(model=models.PeerGroup)

    class Meta(BaseTable.Meta):
        model = models.PeerGroup
        fields = (
            "pk",
            "name",
            "peergroup_template",
            "routing_instance",
            "enabled",
            "role",
            "autonomous_system",
            "import_policy",
            "export_policy",
            "source_ip",
            "source_interface",
            "secret",
        )
        default_columns = (
            "pk",
            "name",
            "peergroup_template",
            "routing_instance",
            "enabled",
            "role",
            "autonomous_system",
            "import_policy",
            "export_policy",
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
            "import_policy",
            "export_policy",
            "secret",
        )
        default_columns = (
            "pk",
            "name",
            "enabled",
            "role",
            "autonomous_system",
            "import_policy",
            "export_policy",
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
            "import_policy",
            "export_policy",
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
            "import_policy",
            "export_policy",
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
            "import_policy",
            "export_policy",
            "multipath",
        )
        default_columns = (
            "pk",
            "address_family",
            "routing_instance",
            "afi_safi",
            "vrf",
            "import_policy",
            "export_policy",
            "multipath",
            "actions",
        )
