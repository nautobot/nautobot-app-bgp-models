"""Django model definitions for nautobot_bgp_models."""

import functools
from django.core.exceptions import ValidationError

from django.db import models
from django.urls import reverse
from nautobot.circuits.models import Provider
from nautobot.core.models.generics import PrimaryModel, OrganizationalModel
from nautobot.dcim.fields import ASNField
from nautobot.extras.models import StatusModel
from nautobot.extras.utils import extras_features
from nautobot.utilities.choices import ChoiceSet
from nautobot.utilities.choices import ColorChoices
from nautobot.utilities.fields import ColorField
from nautobot.ipam.models import IPAddress


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
    def get_inherited_field(self, field_name, inheritance_path=None):
        """returns value, inheritance_indicator, inheritance_source"""

        field_value = getattr(self, field_name, None)
        if field_value:
            return field_value, False, None
        else:
            if inheritance_path is None and field_name in getattr(self, inheritance_path, {}):
                inheritance_path = self.inheritance_path[field_name]
            for path_element in (inheritance_path or []):
                field_value = rgetattr(self, path_element, None)

                if field_value:
                    obj = rgetattr(self, ".".join(path_element.split('.')[:-1]), None)
                    return field_value, True, obj
            else:
                return None, False, None

    def get_fields(self, include_inherited=False):
        """
        Class Fields Getter.

        Traverse field_name_inheritance list contained in self.field to inherit BGP attributes as declared in inheritance path.
        """
        result = {}

        for field_name, field_inheritance in self.property_inheritance.items():
            inheritance_path = field_inheritance if include_inherited else []
            inheritance_result = self.get_inherited_field(field_name=field_name, inheritance_path=inheritance_path)
            result[field_name] = {
                    "value": inheritance_result[0],
                    "inherited": inheritance_result[1],
                    "source": inheritance_result[2]
                }

        return result

    class Meta:
        abstract = True


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
    """Autonomous System information."""

    asn = ASNField(unique=True, verbose_name="ASN", help_text="32-bit autonomous system number")
    description = models.CharField(max_length=200, blank=True)
    provider = models.ForeignKey(to=Provider, on_delete=models.PROTECT, blank=True, null=True)

    csv_headers = ["asn", "description", "status"]

    class Meta:
        ordering = ["asn"]
        verbose_name = "Autonomous system"

    def __str__(self):
        """String representation of an AutonomousSystem."""
        return f"AS {self.asn}"

    def get_absolute_url(self):
        """Get the URL for detailed view of a single AutonomousSystem."""
        return reverse("plugins:nautobot_bgp_models:autonomoussystem", args=[self.pk])

    def to_csv(self):
        """Render an AutonomousSystem record to CSV fields."""
        return self.asn, self.description, self.get_status_display()


@extras_features(
    "custom_fields",
    "custom_links",
    "custom_validators",
    "export_templates",
    "graphql",
    "relationships",
    "webhooks",
)
class PeeringRole(OrganizationalModel):  # TODO(mzb): consider renaming to `BGPRole`
    """Role definition for use with a PeerGroup or PeerEndpoint."""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    color = ColorField(default=ColorChoices.COLOR_GREY)
    description = models.CharField(max_length=200, blank=True)

    csv_headers = ["name", "slug", "color", "description"]

    class Meta:
        verbose_name = "BGP Role"

    def __str__(self):
        """String representation of a PeeringRole."""
        return self.name

    def get_absolute_url(self):
        """Get the URL for a detailed view of a single PeeringRole."""
        return reverse("plugins:nautobot_bgp_models:peeringrole", args=[self.pk])

    def to_csv(self):
        """Render a PeeringRole record to CSV fields."""
        return (self.name, self.slug, self.color, self.description)


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

    # TODO(mzb): add *name* attr, unique on device.
    role = models.ForeignKey(to=PeeringRole, on_delete=models.PROTECT, related_name="routing_instances", blank=True, null=True)

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

    autonomous_system = models.ForeignKey(  # TODO(mzb): should this be mandatory ?
        to=AutonomousSystem,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
    )

    def get_absolute_url(self):
        """Get the URL for detailed view of a single AutonomousSystem."""
        return reverse("plugins:nautobot_bgp_models:bgproutinginstance", args=[self.pk])

    def __str__(self):
        """String representation of a Routing Instance."""
        return f"{self.device} - {self.autonomous_system}"

    class Meta:
        verbose_name = "BGP Routing Instance"


class PeerGroupTemplate(PrimaryModel, StatusModel, BGPMixin):
    """BGP peer group information."""
    #    def clean(self):
    #     - local-address on routing_instance
    #
    property_inheritance = {  # TODO(mzb): Document, if null still used by `.get_fields()`
        "auth_password": [],
        "autonomous_system": [],
        "description": [],
        "enabled": [],
        "export_policy": [],
        "import_policy": [],
        "ip": [],
    }

    name = models.CharField(max_length=100)

    role = models.ForeignKey(to=PeeringRole, on_delete=models.PROTECT, related_name="peer_group_templates", blank=True,
                             null=True)

    description = models.CharField(max_length=200, blank=True)

    enabled = models.BooleanField(default=True)

    autonomous_system = models.ForeignKey(
        to=AutonomousSystem,
        blank=True,
        null=True,
        related_name="peer_group_template_local_as",
        on_delete=models.PROTECT,
    )

    import_policy = models.CharField(max_length=100, default="", blank=True)

    export_policy = models.CharField(max_length=100, default="", blank=True)

    auth_password = models.CharField(max_length=200, blank=True, default="")

    def __str__(self):
        return f"Peer Group Template {self.name}"

    def get_absolute_url(self):
        """Get the URL for detailed view of a single AutonomousSystem."""
        return reverse("plugins:nautobot_bgp_models:peergrouptemplate", args=[self.pk])

    class Meta:
        unique_together = [("name")]
        verbose_name = "BGP Peer Group Template"


class PeerGroup(PrimaryModel, StatusModel, BGPMixin):
    """BGP peer group information."""

    # TODO(mzb): add local-ip / update-source support.

    #    def clean(self):
    #     - local-address on routing_instance

    property_inheritance = {
        "auth_password": [
            "template.auth_password",
        ],
        "autonomous_system": [
            "template.autonomous_system",
            "routing_instance.autonomous_system",
        ],
        "description": [
            "template.description",
        ],
        "enabled": [
            "template.enabled",
        ],
        "export_policy": [
            "template.export_policy"
        ],
        "import_policy": [
            "template.import_policy",
        ],
        "ip": [],
        # "remote_autonomous_system": [],
    }

    template = models.ForeignKey(to=PeerGroupTemplate, on_delete=models.PROTECT, related_name="peer_groups", blank=True, null=True)

    name = models.CharField(max_length=100)

    role = models.ForeignKey(to=PeeringRole, on_delete=models.PROTECT, related_name="peer_groups", blank=True, null=True)

    description = models.CharField(max_length=200, blank=True)

    enabled = models.BooleanField(default=True)

    routing_instance = models.ForeignKey(
        to=BGPRoutingInstance,
        on_delete=models.CASCADE,
        related_name="bgp_peer_groups",  # TODO(mzb)
        verbose_name="Routing Instance",
    )

    autonomous_system = models.ForeignKey(
        to=AutonomousSystem,
        blank=True,
        null=True,
        related_name="peer_group_local_as",
        on_delete=models.PROTECT,
    )

    import_policy = models.CharField(max_length=100, default="", blank=True)

    export_policy = models.CharField(max_length=100, default="", blank=True)

    auth_password = models.CharField(max_length=200, blank=True, default="")

    def __str__(self):
        return f"Peer Group {self.name}"

    def get_absolute_url(self):
        """Get the URL for detailed view of a single AutonomousSystem."""
        return reverse("plugins:nautobot_bgp_models:peergroup", args=[self.pk])

    class Meta:
        unique_together = [("name", "routing_instance")]
        verbose_name = "BGP Peer Group"


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

    property_inheritance = {
        "auth_password": [
            "peer_group.auth_password",
        ],
        "autonomous_system": [
            "peer_group.autonomous_system",
            "routing_instance.autonomous_system",
        ],
        "description": [],
        "enabled": [],
        "export_policy": [
            "peer_group.export_policy",
        ],
        "import_policy": [
            "peer_group.import_policy",
        ],
        "ip": [
            "peer_group.ip",
        ],
    }

    description = models.CharField(max_length=200, blank=True)

    role = models.ForeignKey(to=PeeringRole, on_delete=models.PROTECT, related_name="peer_endpoints", blank=True, null=True)

    enabled = models.BooleanField(default=True)

    routing_instance = models.ForeignKey(
        to=BGPRoutingInstance,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="bgp_peer_endpoint_routing_instances",
        verbose_name="BGP Routing Instance",
    )

    # TODO(mzb)
    # @property
    # def _ip(self):
    #     # if self.update_source:
    #     #     pass
    #     if self.ip:
    #         return self.ip

    ip = models.ForeignKey(  # local-address
        to="ipam.IPAddress",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="bgp_peer_endpoint_ips",
        verbose_name="BGP Peer IP",
    )

    autonomous_system = models.ForeignKey(
        to=AutonomousSystem,
        blank=True,
        null=True,
        related_name="peer_endpoint_local_as",
        on_delete=models.PROTECT,
    )

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
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )

    import_policy = models.CharField(max_length=100, default="", blank=True)

    export_policy = models.CharField(max_length=100, default="", blank=True)

    auth_password = models.CharField(max_length=200, blank=True, default="")

    def __str__(self):
        if self.routing_instance and self.routing_instance.device:
            return f"{self.routing_instance.device}"
        else:
            return f"{self.ip} ({self.autonomous_system})"

    def get_absolute_url(self):
        """Get the URL for detailed view of a single AutonomousSystem."""
        return reverse("plugins:nautobot_bgp_models:peerendpoint", args=[self.pk])

    def clean(self):
        if not self.routing_instance:
            if (not self.ip) or (not self.autonomous_system):
                raise ValidationError("Must specify both IP & ASN for non-local peers.")

        if self.routing_instance:
            if self.ip not in IPAddress.objects.filter(interface__device_id=self.routing_instance.device.id):
                raise ValidationError("Peer IP not associated with Routing Instance")

        # ensure IP object is related to the routing instance. (if routing instance declared.)
        # ensure local IP is set either on self. either on self.peer_group.
        #  - add validation on PeerGroup while removing self.ipaddress -> check related Endpoints.
        # ensure if no ASN is set, routing instance is set.
        # ensure self.session has no more than > endpoints !.
        # ensure one of : [ self.ip , self.update_source_interface ]
        # ensure selected Peer Group is associated to the Routing Instance


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

    role = models.ForeignKey(to=PeeringRole, on_delete=models.PROTECT, blank=True, null=True)

    authentication_key = models.CharField(max_length=200, blank=True, default="")

    class Meta:
        verbose_name = "BGP peer session"

    @property
    def endpoint_a(self):
        """Get the "first" endpoint associated with this PeerSession."""
        return self.endpoints.all()[0] if self.endpoints.exists() else None

    @property
    def endpoint_z(self):
        """Get the "second" endpoint associated with this PeerSession."""
        return self.endpoints.all()[1] if self.endpoints.count() > 1 else None

    def __str__(self):
        """String representation of a single PeerSession."""
        return f"{self.endpoint_a} ↔︎ {self.endpoint_z}"

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
        verbose_name = "BGP address family"
        verbose_name_plural = "BGP Address Families"

    def __str__(self):
        """String representation of a single AddressFamily."""
        if self.vrf:
            return f"AFI-SAFI {self.afi_safi} in vrf '{self.vrf}' -> {self.routing_instance.device}"
        else:
            return f"AFI-SAFI {self.afi_safi} -> {self.routing_instance.device}"

    def get_absolute_url(self):
        """Get the URL for a detailed view of a single PeerSession."""
        return reverse("plugins:nautobot_bgp_models:addressfamily", args=[self.pk])

    # TODO(mzb): Enforce Peer IPs to be in VRFs ?


@extras_features(
    "custom_fields",
    "custom_links",
    "custom_validators",
    "export_templates",
    "graphql",
    "relationships",
    "webhooks",
)
class PeerGroupContext(PrimaryModel, StatusModel, BGPMixin):
    """Peer Endpoint's Address Family Context."""
    property_inheritance = {
        "export_policy": [
            "address_family.export_policy",
            "peer_group.export_policy",
        ],
        "import_policy": [
            "address_family.import_policy",
            "peer_group.import_policy",
        ],
        "multipath": [
            "address_family.multipath",
            "peer_group.multipath"
        ],
    }

    peer_group = models.ForeignKey(
        to=PeerGroup,
        on_delete=models.CASCADE,
    )

    address_family = models.ForeignKey(
        to=AddressFamily,
        on_delete=models.PROTECT,
    )

    multipath = models.BooleanField(blank=True, null=True)

    import_policy = models.CharField(max_length=100, default="", blank=True)

    export_policy = models.CharField(max_length=100, default="", blank=True)


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
    property_inheritance = {
        "export_policy": [
            "address_family.export_policy",
            "peer_endpoint.export_policy",
            "peer_endpoint.peer_group.export_policy",
        ],
        "import_policy": [
            "address_family.import_policy",
            "peer_endpoint.import_policy",
            "peer_endpoint.peer_group.import_policy",
        ],
        "maximum_prefix": [
            "address_family.maximum_prefix",
            "peer_endpoint.maximum_prefix",
            "peer_endpoint.peer_group.maximum_prefix",
        ],
    }

    peer_endpoint = models.ForeignKey(
        to=PeerEndpoint,
        on_delete=models.CASCADE,
    )

    address_family = models.ForeignKey(
        to=AddressFamily,
        on_delete=models.PROTECT,
    )

    maximum_prefix = models.IntegerField(blank=True, null=True)

    import_policy = models.CharField(max_length=100, default="", blank=True)

    export_policy = models.CharField(max_length=100, default="", blank=True)

    class Meta:
        unique_together = [("peer_endpoint", "address_family")]
        verbose_name = "BGP Peer-Endpoint Context"
        verbose_name_plural = "BGP Peer-Endpoint Contexts"

    def get_absolute_url(self):
        """Get the URL for detailed view of a single AutonomousSystem."""
        return reverse("plugins:nautobot_bgp_models:peerendpointcontext", args=[self.pk])
