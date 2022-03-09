"""Django model definitions for nautobot_bgp_models."""

import functools
# from . import choices
from collections import OrderedDict

from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.urls import reverse
from nautobot.core.models.generics import PrimaryModel, OrganizationalModel
from nautobot.dcim.fields import ASNField
from nautobot.extras.models import StatusModel
from nautobot.extras.utils import extras_features
from nautobot.utilities.choices import ChoiceSet
from nautobot.utilities.utils import deepmerge


def rgetattr(obj, attr, *args):
    def _getattr(obj, attr):
        return getattr(obj, attr, *args)
    return functools.reduce(_getattr, [obj] + attr.split('.'))


class AFISAFIChoices(ChoiceSet):
    """Choices for the "afi_safi" field on the AddressFamily model."""

    AFI_IPV4 = "ipv4"
    AFI_IPV4_FLOWSPEC = "ipv4_flowspec"
    AFI_VPNV4 = "vpnv4"
    AFI_IPV6_LU = "ipv6_labeled_unicast"

    CHOICES = (
        (AFI_IPV4, "IPv4"),
        (AFI_IPV4_FLOWSPEC, "IPv4 FlowSpec"),
        (AFI_VPNV4, "VPNv4"),
        (AFI_IPV6_LU, "IPv6 Labeled Unicast"),
    )


class BGPMixin(models.Model):
    def get_inherited_field(self, field_name, inheritance_path):
        """returns field_value, inheritance_indicator"""

        field_value = getattr(self, field_name, None)
        if field_value:
            return field_value, False

        for path_element in (inheritance_path or []):
            field_value = rgetattr(self, path_element, None)

            if field_value:
                return field_value, True

        return None, False

    def get_fields(self, include_inherited=False):
        """
        Class Fields Getter.

        Traverse field_name_inheritance list contained in self.field to inherit BGP attributes as declared in inheritance path.
        """
        result = {}

        for field_name in self.fields:
            inheritance_path = getattr(self, f"{field_name}_inheritance", None) if include_inherited else []
            inheritance_result = self.get_inherited_field(field_name=field_name, inheritance_path=inheritance_path)

            result.update(
                field_name={"value": inheritance_result[0], "inherited": inheritance_result[1]}
            )

        return result

    class Meta:
        abstract = True


##  DRAFT of config context inheritance for BGP attributes.

# class BGPConfigContextMixin(models.Model):
#     local_context_data = models.JSONField(
#         encoder=DjangoJSONEncoder,
#         blank=True,
#         null=True,
#     )
#
#     @property
#     def get_context_paths(self):
#         return [rgetattr(self, x, None) for x in self.local_context_path]
#
#     def get_config_context(self):
#         # always manually query for config contexts
#         config_context_data = [x for x in self.get_context_paths if x]
#
#         # Compile all config data, overwriting lower-weight values with higher-weight values where a collision occurs
#         data = OrderedDict()
#         for context in config_context_data:
#             data = deepmerge(data, context)
#
#         # If the object has local config context data defined, merge it last
#         if self.local_context_data:
#             data = deepmerge(data, self.local_context_data)
#
#         return data
#
#     class Meta:
#         abstract = True


@extras_features(
    "custom_fields",
    "custom_links",
    "custom_validators",
    "export_templates",
    "graphql",
    "relationships",
    "statuses",
    "webhooks",
)
class AutonomousSystem(PrimaryModel, StatusModel):
    """BGP Autonomous System information."""

    asn = ASNField(unique=True, verbose_name="ASN", help_text="32-bit autonomous system number")
    description = models.CharField(max_length=200, blank=True)

    csv_headers = ["asn", "description", "status"]

    class Meta:
        ordering = ["asn"]
        verbose_name = "BGP autonomous system"

    def __str__(self):
        """String representation of an AutonomousSystem."""
        return f"AS {self.asn}"

    def get_absolute_url(self):
        """Get the URL for detailed view of a single AutonomousSystem."""
        return reverse("plugins:nautobot_bgp_models:autonomoussystem", args=[self.pk])

    def to_csv(self):
        """Render an AutonomousSystem record to CSV fields."""
        return (self.asn, self.description, self.get_status_display())


@extras_features(
    "custom_fields",
    "custom_links",
    "custom_validators",
    "export_templates",
    "graphql",
    "relationships",
    "statuses",
    "webhooks",
)
class BGPRoutingInstance(PrimaryModel, StatusModel):
    """BGP Routing Instance"""

    # local_context_path = [
    #     "parent_template.local_context_data",
    # ]

    # is_template = models.BooleanField(blank=True, null=True)
    # parent_template = models.ForeignKey(
    #     to="self",
    #     on_delete=models.SET_NULL,
    #     blank=True,
    #     null=True,
    # )

    description = models.CharField(max_length=200, blank=True)

    device = models.ForeignKey(
        to="dcim.Device",
        on_delete=models.PROTECT,
        related_name="bgp_routing_instances",
        verbose_name="Device",
    )

    router_id = models.ForeignKey(
        to="ipam.IPAddress",
        verbose_name="Router ID",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
    )

    autonomous_system = models.ForeignKey(
        to=AutonomousSystem,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
    )

    def get_absolute_url(self):
        """Get the URL for detailed view of a single AutonomousSystem."""
        return reverse("plugins:nautobot_bgp_models:bgproutinginstance", args=[self.pk])


class PeerGroup(PrimaryModel, StatusModel):
    """BGP peer group information."""

    name = models.CharField(max_length=100)

    # is_template = models.BooleanField(blank=True, null=True)
    # parent_template = models.ForeignKey(
    #     to="self",
    #     on_delete=models.SET_NULL,
    #     blank=True,
    #     null=True,
    # )

    routing_instance = models.ForeignKey(
        to=BGPRoutingInstance,
        on_delete=models.CASCADE,
        related_name="bgp_peer_groups",
        verbose_name="Peer group",
    )

    autonomous_system = models.ForeignKey(
        to=AutonomousSystem,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
    )

    remote_autonomous_system = models.ForeignKey(  # optional
        to=AutonomousSystem,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
    )

    ip = models.ForeignKey(  # local-address
        to="ipam.IPAddress",
        on_delete=models.PROTECT,
        related_name="bgp_peer_group_ips",
        verbose_name="BGP Peer Group IP",
    )

    auth_password = models.CharField(max_length=200, blank=True, default="")

    fields = [
        "name",
        "routing_instance",
        "autonomous_system",
        "remote_autonomous_system",
        "ip",
        "auth_password",
    ]

#    def clean(self):
#     - local-address on routing_instance


@extras_features(
    "custom_fields",
    "custom_links",
    "custom_validators",
    "export_templates",
    "relationships",
    "webhooks",
)
class PeerEndpoint(PrimaryModel, StatusModel, BGPMixin):
    """BGP information about one endpoint of a peering session."""
    description = models.CharField(max_length=200, blank=True)
    enabled = models.BooleanField(default=True)

    routing_instance = models.ForeignKey(
        to=BGPRoutingInstance,
        on_delete=models.CASCADE,
        related_name="bgp_peer_endpoint_routing_instances",
        verbose_name="Device",
    )

    ip = models.ForeignKey(  # local-address
        to="ipam.IPAddress",
        on_delete=models.PROTECT,
        related_name="bgp_peer_endpoint_ips",
        verbose_name="BGP Peer IP",
    )
    ip_inheritance = [
        "peer_group.ip",
    ]

    autonomous_system = models.ForeignKey(
        to=AutonomousSystem,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
    )
    autonomous_system_inheritance = [
        "routing_instance.autonomous_system",
        "peer_group.autonomous_system",
    ]

    remote_autonomous_system = models.ForeignKey(  # optional override.
        to=AutonomousSystem,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    remote_autonomous_system_inheritance = [
        "peer.routing_instance.autonomous_system",
        "peer.peer_group.autonomous_system",
        "peer.autonomous_system",
        "peer_group.remote_autonomous_system",
    ]

    peer = models.ForeignKey(
        to="self",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    session = models.ForeignKey(
        to="PeerSession",
        on_delete=models.CASCADE,
        related_name="endpoints",
    )

    peer_group = models.ForeignKey(
        to=PeerGroup,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    import_policy = models.CharField(max_length=100, default="", blank=True)
    import_policy_inheritance = [
        "routing_instance.import_policy",
        "peer_group.import_policy",
    ]

    export_policy = models.CharField(max_length=100, default="", blank=True)
    export_policy_inheritance = [
        "routing_instance.export_policy",
        "peer_group.export_policy",
    ]

    auth_password = models.CharField(max_length=200, blank=True, default="")
    auth_password_inheritance = [
        "peer_group.auth_password",
    ]

    fields = [
        "enabled",
        "description",
        "autonomous_system",
        "remote_autonomous_system",
        "import_policy",
        "export_policy",
        "auth_password"
    ]


@extras_features(
    "custom_fields",
    "custom_links",
    "custom_validators",
    "export_templates",
    "graphql",
    "relationships",
    "statuses",
    "webhooks",
)
class PeerSession(OrganizationalModel, StatusModel):
    """Linkage between two PeerEndpoint records."""

    # role = models.ForeignKey(to=PeeringRole, on_delete=models.PROTECT)

    authentication_key = models.CharField(max_length=200, blank=True, default="")

    class Meta:
        verbose_name = "BGP peer session"

    def endpoint_a(self):
        """Get the "first" endpoint associated with this PeerSession."""
        return self.endpoints.all()[0] if self.endpoints.exists() else None

    def endpoint_z(self):
        """Get the "second" endpoint associated with this PeerSession."""
        return self.endpoints.all()[1] if self.endpoints.count() > 1 else None

    def __str__(self):
        """String representation of a single PeerSession."""
        return f"{self.endpoint_a()} ↔︎ {self.endpoint_z()}"

    def get_absolute_url(self):
        """Get the URL for a detailed view of a single PeerSession."""
        return reverse("plugins:nautobot_bgp_models:peersession", args=[self.pk])

    def update_peers(self):
        """Update peer field for both PeerEndpoints."""
        endpoints = self.endpoints.all()
        if len(endpoints) < 2:
            return None
        if endpoints[0].peer == endpoints[1] and endpoints[1].peer == endpoints[0]:
            return False

        endpoints[0].peer = endpoints[1]
        endpoints[1].peer = endpoints[0]
        endpoints[0].validated_save()
        endpoints[1].validated_save()
        return True


@extras_features(
    "custom_fields",
    "custom_links",
    "custom_validators",
    "export_templates",
    "graphql",
    "relationships",
    "webhooks",
)
class AddressFamily(OrganizationalModel, StatusModel, BGPMixin):
    """Address-family (AFI-SAFI) model."""

    afi_safi = models.CharField(max_length=64, choices=AFISAFIChoices, verbose_name="AFI-SAFI")

    # is_template = models.BooleanField(blank=True, null=True)
    # parent_template = models.ForeignKey(
    #     to="self",
    #     on_delete=models.PROTECT,
    #     blank=True,
    #     null=True,
    # )

    vrf = models.ForeignKey(
        to="ipam.VRF",
        verbose_name="VRF",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
    )

    routing_instance = models.ForeignKey(
        to=BGPRoutingInstance,
        on_delete=models.CASCADE,
        related_name="bgp_address_families",
        verbose_name="BGP Routing Instance",
    )

    import_policy = models.CharField(max_length=100, default="", blank=True)
    export_policy = models.CharField(max_length=100, default="", blank=True)
    multipath = models.BooleanField(blank=True, null=True)

    class Meta:
        ordering = ["-routing_instance", "-vrf"]
        unique_together = [("afi_safi", "routing_instance", "vrf")]
        verbose_name = "BGP address-family"
        verbose_name_plural = "BGP address-families"

    def __str__(self):
        """String representation of a single AddressFamily."""

        return f"AFI-SAFI {self.afi_safi} on BGP {self.routing_instance.device}"


@extras_features(
    "custom_fields",
    "custom_links",
    "custom_validators",
    "export_templates",
    "graphql",
    "relationships",
    "webhooks",
)
class PeerEndpointContext(PrimaryModel, StatusModel, BGPMixin):
    """Peer Endpoint's Address Family Context."""

    peer_endpoint = models.ForeignKey(
        to=PeerEndpoint,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    address_family = models.ForeignKey(
        to=AddressFamily,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )

    maximum_prefix = models.IntegerField(blank=True, null=True)
    maximum_prefix_inheritance = [
        # "peer_endpoint.peer_group.parent_template.import_policy",
        "peer_endpoint.peer_group.maximum_prefix",
        "peer_endpoint.maximum_prefix",
        "address_family.maximum_prefix",
    ]

    multipath = models.BooleanField(blank=True, null=True)
    multipath_inheritance = [
        # "peer_endpoint.peer_group.parent_template.import_policy",
        "peer_endpoint.peer_group.multipath",
        "peer_endpoint.multipath",
        "address_family.multipath",
    ]

    import_policy = models.CharField(max_length=100, default="", blank=True)
    import_policy_inheritance = [
        # "peer_endpoint.peer_group.parent_template.import_policy",
        "peer_endpoint.peer_group.import_policy",
        "peer_endpoint.import_policy",
        "address_family.import_policy",
    ]

    export_policy = models.CharField(max_length=100, default="", blank=True)
    export_policy_inheritance = [
        # "peer_endpoint.peer_group.parent_template.export_policy",
        "peer_endpoint.peer_group.export_policy",
        "peer_endpoint.export_policy",
        "address_family.export_policy",
    ]

    class Meta:
        unique_together = [("peer_endpoint", "address_family")]
        verbose_name = "BGP Peer-Endpoint Context"
        verbose_name_plural = "BGP Peer-Endpoint Contexts"
