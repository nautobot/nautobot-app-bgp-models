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
    tags = TagColumn(url_name="plugins:nautobot_bgp_models:autonomoussystem_list")
    actions = ButtonsColumn(model=models.AutonomousSystem)

    class Meta(BaseTable.Meta):
        model = models.AutonomousSystem
        fields = ("pk", "asn", "status", "description", "tags")
        default_columns = ("pk", "asn", "status", "description", "tags")


class PeeringRoleTable(BaseTable):
    """Table representation of PeeringRole records."""

    pk = ToggleColumn()
    name = tables.LinkColumn()
    color = ColorColumn()
    actions = ButtonsColumn(model=models.PeeringRole)

    class Meta(BaseTable.Meta):
        model = models.PeeringRole
        fields = (
            "pk",
            "name",
            "slug",
            "color",
            "description",
        )


class AbstractPeeringInfoTable(BaseTable):
    """Common parent of PeerGroupTable and PeeringEndpointTable."""

    pk = ToggleColumn()
    enabled = BooleanColumn()
    vrf = tables.LinkColumn()
    update_source = tables.LinkColumn(verbose_name="Update source")
    router_id = tables.LinkColumn()
    autonomous_system = tables.LinkColumn()
    multipath = BooleanColumn()
    bfd_fast_detection = BooleanColumn()
    enforce_first_as = BooleanColumn()
    send_community = BooleanColumn()

    class Meta(BaseTable.Meta):
        fields = (
            "description",
            "enabled",
            "vrf",
            "update_source",
            "router_id",
            "autonomous_system",
            "maximum_paths_ibgp",
            "maximum_paths_ebgp",
            "maximum_paths_eibgp",
            "maximum_prefix",
            "bfd_multiplier",
            "bfd_minimum_interval",
            "bfd_fast_detection",
            "enforce_first_as",
            "send_community_ebgp",
        )
        default_columns = ("enabled", "vrf", "autonomous_system", "actions")


class PeerGroupTable(AbstractPeeringInfoTable):
    """Table representation of PeerGroup records."""

    device = tables.LinkColumn()
    name = tables.LinkColumn()
    role = ColoredLabelColumn()
    actions = ButtonsColumn(model=models.PeerGroup)

    class Meta(AbstractPeeringInfoTable.Meta):
        model = models.PeerGroup
        fields = (
            "pk",
            "device",
            "name",
            "role",
            *AbstractPeeringInfoTable.Meta.fields,
        )
        default_columns = ("pk", "device", "name", "role", *AbstractPeeringInfoTable.Meta.default_columns)


class PeerEndpointTable(AbstractPeeringInfoTable):
    """Table representation of PeerEndpoint records."""

    endpoint = tables.LinkColumn(
        viewname="plugins:nautobot_bgp_models:peerendpoint",
        args=[A("pk")],
        text=str,
    )
    device = tables.LinkColumn()
    local_ip = tables.LinkColumn()
    peer = tables.LinkColumn()
    actions = ButtonsColumn(model=models.PeerEndpoint)

    class Meta(AbstractPeeringInfoTable.Meta):
        model = models.PeerEndpoint
        fields = (
            "pk",
            "endpoint",
            "peer_group",
            "local_ip",
            "peer",
            *AbstractPeeringInfoTable.Meta.fields,
        )
        default_columns = (
            "pk",
            "endpoint",
            "peer_group",
            "local_ip",
            "peer",
            *AbstractPeeringInfoTable.Meta.default_columns,
        )


class PeerSessionTable(BaseTable):
    """Table representation of PeerSession records."""

    pk = ToggleColumn()
    session = tables.LinkColumn(
        viewname="plugins:nautobot_bgp_models:peersession",
        args=[A("pk")],
        text=str,
    )
    endpoint_a = tables.LinkColumn()
    endpoint_z = tables.LinkColumn()
    role = ColoredLabelColumn()
    status = ColoredLabelColumn()
    actions = ButtonsColumn(model=models.PeerSession)

    class Meta(BaseTable.Meta):
        model = models.PeerSession
        fields = (
            "pk",
            "session",
            "endpoint_a",
            "endpoint_z",
            "role",
            "status",
        )


class AddressFamilyTable(BaseTable):
    """Table representation of AddressFamily records."""

    pk = ToggleColumn()
    device = tables.LinkColumn()
    afi_safi = tables.LinkColumn()
    peer_group = tables.LinkColumn()
    peer_endpoint = tables.LinkColumn()
    actions = ButtonsColumn(model=models.AddressFamily)

    class Meta(BaseTable.Meta):
        model = models.AddressFamily
        fields = (
            "pk",
            "afi_safi",
            "device",
            "peer_group",
            "peer_endpoint",
            "maximum_prefix",
            "multipath",
        )
        default_columns = (
            "pk",
            "afi_safi",
            "device",
            "peer_group",
            "peer_endpoint",
        )
