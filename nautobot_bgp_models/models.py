"""BGP data models."""
import functools
from collections import OrderedDict

from django.core.exceptions import ValidationError
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.urls import reverse
from nautobot.circuits.models import Provider
from nautobot.core.fields import AutoSlugField
from nautobot.core.models.generics import PrimaryModel, OrganizationalModel
from nautobot.dcim.fields import ASNField
from nautobot.extras.models import StatusModel
from nautobot.extras.utils import extras_features
from nautobot.ipam.models import IPAddress
from nautobot.utilities.choices import ColorChoices
from nautobot.utilities.fields import ColorField
from nautobot.utilities.utils import deepmerge

from nautobot_bgp_models.choices import AFISAFIChoices


def rgetattr(obj, attr, *args):
    """Recursive getattr helper."""

    def _getattr(obj, attr):
        return getattr(obj, attr, *args)

    return functools.reduce(_getattr, [obj] + attr.split("."))


class InheritanceMixin(models.Model):
    """BGP common mixin class."""

    def get_inherited_field(self, field_name, inheritance_path=None):
        """Returns value, inheritance_indicator, inheritance_source."""
        field_value = getattr(self, field_name, None)
        if field_value:
            return field_value, False, None

        if inheritance_path is None and field_name in getattr(self, "property_inheritance", {}):
            inheritance_path = self.property_inheritance[field_name]

        for path_element in inheritance_path or []:
            _path_element = f"{path_element}.{field_name}"  # Append the field name to each path element.
            field_value = rgetattr(self, _path_element, None)

            if field_value:
                obj = rgetattr(self, ".".join(_path_element.split(".")[:-1]), None)
                return field_value, True, obj

        return None, False, None

    def get_fields(self, include_inherited=False):
        """
        Class Fields Getter.

        Get object's inherited fields as defined in self.property_inheritance.
        """
        result = {}

        for field_name, field_inheritance in self.property_inheritance.items():
            inheritance_path = field_inheritance if include_inherited else []
            inheritance_result = self.get_inherited_field(field_name=field_name, inheritance_path=inheritance_path)
            result[field_name] = {
                "value": inheritance_result[0],
                "inherited": inheritance_result[1],
                "source": inheritance_result[2],
            }

        return result

    @property
    def fields_inherited(self):
        """Wrapper intended to remove function call with attributes from within a jinja template."""
        return self.get_fields(include_inherited=True)

    class Meta:
        abstract = True


class BGPExtraAttributesMixin(models.Model):
    """BGP Extra Attributes Mixin."""

    extra_attributes = models.JSONField(
        encoder=DjangoJSONEncoder,
        blank=True,
        null=True,
        verbose_name="Extra Attributes",
        help_text="Additional BGP attributes (JSON format)",
    )

    @property
    def get_extra_attributes_paths(self):
        """Get all object paths of inheritable extra attributes."""
        if hasattr(self, "extra_attributes_inheritance"):
            paths = self.extra_attributes_inheritance
        else:
            paths = []

        return [rgetattr(self, f"{x}.extra_attributes", None) for x in paths]

    def get_extra_attributes(self):
        """Render extra attributes for an object."""
        # always manually query for extra attributes
        extra_attributes_data = [x for x in self.get_extra_attributes_paths if x]

        # Compile all extra attributes, overwriting lower-weight values with higher-weight values where a collision occurs
        data = OrderedDict()

        for extra_attributes in extra_attributes_data:
            data = deepmerge(data, extra_attributes)

        # If the object has local extra attributes data defined, merge it last
        if self.extra_attributes:
            data = deepmerge(data, self.extra_attributes)
        return data

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

    csv_headers = ["asn", "description", "status", "provider"]

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
        return self.asn, self.description, self.get_status_display(), self.provider


@extras_features(
    "custom_fields",
    "custom_links",
    "custom_validators",
    "export_templates",
    "graphql",
    "relationships",
    "webhooks",
)
class PeeringRole(OrganizationalModel):
    """Role definition for use with a PeerGroup or PeerEndpoint."""

    name = models.CharField(max_length=100, unique=True)
    slug = AutoSlugField(populate_from="name")
    color = ColorField(default=ColorChoices.COLOR_GREY)
    description = models.CharField(max_length=200, blank=True)

    csv_headers = ["name", "slug", "color", "description"]

    class Meta:
        verbose_name = "BGP Peering Role"

    def __str__(self):
        """String representation of a PeeringRole."""
        return self.name

    def get_absolute_url(self):
        """Get the URL for a detailed view of a single PeeringRole."""
        return reverse("plugins:nautobot_bgp_models:peeringrole", args=[self.slug])

    def to_csv(self):
        """Render a PeeringRole record to CSV fields."""
        return self.name, self.slug, self.color, self.description


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
class BGPRoutingInstance(PrimaryModel, StatusModel, BGPExtraAttributesMixin):
    """BGP instance definition."""

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
        on_delete=models.PROTECT,
    )

    csv_headers = [
        "device",
        "autonomous_system",
        "router_id",
        "status",
        "description",
    ]

    def get_absolute_url(self):
        """Get the URL for detailed view of a single BGPRoutingInstance."""
        return reverse("plugins:nautobot_bgp_models:bgproutinginstance", args=[self.pk])

    def __str__(self):
        """String representation of a BGPRoutingInstance."""
        return f"{self.device} - {self.autonomous_system}"

    class Meta:
        verbose_name = "BGP Routing Instance"
        unique_together = [("device", "autonomous_system")]

    def to_csv(self):
        """Render an BGPRoutingInstance record to CSV fields."""
        return (
            self.device.identifier if self.device else None,
            self.autonomous_system.asn if self.autonomous_system else None,
            self.router_id.address if self.router_id else None,
            self.get_status_display(),
            self.description,
        )

    def clean(self):
        """Clean."""
        # Ensure .status attribute:
        if not self.status:
            raise ValidationError("Status must be defined for the BGP Routing Instance.")


@extras_features(
    "custom_fields",
    "custom_links",
    "custom_validators",
    "export_templates",
    "graphql",
    "relationships",
    "webhooks",
)
class PeerGroupTemplate(PrimaryModel, BGPExtraAttributesMixin):
    """Model for Peer Group templates."""

    name = models.CharField(max_length=100, unique=True, blank=False)

    enabled = models.BooleanField(default=True)

    role = models.ForeignKey(
        to=PeeringRole, on_delete=models.PROTECT, related_name="peer_group_templates", blank=True, null=True
    )

    description = models.CharField(max_length=200, blank=True)

    autonomous_system = models.ForeignKey(
        to=AutonomousSystem,
        blank=True,
        null=True,
        related_name="peer_group_templates",
        on_delete=models.PROTECT,
    )

    secret = models.ForeignKey(
        to="extras.Secret",
        on_delete=models.PROTECT,
        related_name="bgp_peer_group_templates",
        blank=True,
        null=True,
    )
    csv_headers = ["name", "autonomous_system", "enabled", "role"]

    def to_csv(self):
        """Render a PeerGroupTemplate record to CSV fields."""
        return (
            self.name,
            self.autonomous_system.asn if self.autonomous_system else None,
            self.enabled,
            self.role.name if self.role else None,
        )

    def __str__(self):
        """String."""
        return f"{self.name}"

    def get_absolute_url(self):
        """Get the URL for detailed view of a single PeerGroupTemplate."""
        return reverse("plugins:nautobot_bgp_models:peergrouptemplate", args=[self.pk])

    class Meta:
        verbose_name = "BGP Peer Group Template"


@extras_features(
    "custom_fields",
    "custom_links",
    "custom_validators",
    "export_templates",
    "graphql",
    "relationships",
    "webhooks",
)
class PeerGroup(PrimaryModel, InheritanceMixin, BGPExtraAttributesMixin):
    """BGP peer group information."""

    extra_attributes_inheritance = ["peergroup_template", "routing_instance"]
    property_inheritance = {
        "autonomous_system": ["peergroup_template", "routing_instance"],
        "description": ["peergroup_template"],
        "enabled": ["peergroup_template"],
        "role": ["peergroup_template"],
    }

    name = models.CharField(max_length=100)

    # Rename to avoid clash with DRF renderer
    peergroup_template = models.ForeignKey(
        to=PeerGroupTemplate, on_delete=models.PROTECT, related_name="peer_groups", blank=True, null=True
    )

    role = models.ForeignKey(
        to=PeeringRole, on_delete=models.PROTECT, related_name="peer_groups", blank=True, null=True
    )

    vrf = models.ForeignKey(
        to="ipam.VRF",
        verbose_name="VRF",
        related_name="peer_groups",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
    )

    description = models.CharField(max_length=200, blank=True)

    enabled = models.BooleanField(default=True)

    routing_instance = models.ForeignKey(
        to=BGPRoutingInstance,
        on_delete=models.CASCADE,
        related_name="peer_groups",
        verbose_name="Routing Instance",
    )

    autonomous_system = models.ForeignKey(
        to=AutonomousSystem,
        blank=True,
        null=True,
        related_name="peer_groups",
        on_delete=models.PROTECT,
    )

    source_ip = models.ForeignKey(  # local-address
        to="ipam.IPAddress",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="bgp_peer_groups",
        verbose_name="Source IP Address",
    )

    source_interface = models.ForeignKey(  # update source Interface
        to="dcim.Interface",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="bgp_peer_groups",
        verbose_name="Source Interface",
    )

    secret = models.ForeignKey(
        to="extras.Secret",
        on_delete=models.PROTECT,
        related_name="bgp_peer_groups",
        blank=True,
        null=True,
    )

    csv_headers = [
        "name",
        "routing_instance",
        "autonomous_system",
        "vrf",
        "source_interface",
        "source_ip",
        "peergroup_template",
        "enabled",
        "role",
    ]

    def to_csv(self):
        """Export data."""
        return (
            self.name,
            self.routing_instance.pk,
            self.autonomous_system.asn if self.autonomous_system else None,
            self.vrf.name if self.vrf else None,
            self.source_interface.name if self.source_interface else None,
            self.source_ip.address if self.source_ip else None,
            self.peergroup_template.name if self.peergroup_template else None,
            self.enabled,
            self.role.name if self.role else None,
        )

    def __str__(self):
        """String."""
        if self.vrf:
            return f"{self.name} (VRF {self.vrf}) - {self.routing_instance.device}"
        return f"{self.name} - {self.routing_instance.device}"

    def get_absolute_url(self):
        """Get the URL for detailed view of a single PeerGroup."""
        return reverse("plugins:nautobot_bgp_models:peergroup", args=[self.pk])

    class Meta:
        unique_together = [("name", "routing_instance", "vrf")]
        verbose_name = "BGP Peer Group"

    def clean(self):
        """Clean."""
        # Ensure IP & Update source mutually exclusive:
        if self.source_ip and self.source_interface:
            raise ValidationError("Can not set both IP and Update source options")

        if self.source_interface:
            # Ensure source_interface interface has 1 IP Address assigned
            if self.source_interface.ip_addresses.count() != 1:
                raise ValidationError("Source Interface must have only 1 IP Address assigned.")
            # Ensure VRF membership
            if self.source_interface.ip_addresses.first().vrf != self.vrf:
                raise ValidationError(
                    f"VRF mismatch between PeerGroup VRF ({self.vrf}) "
                    f"and selected source interface VRF ({self.source_interface.ip_addresses.first().vrf})"
                )

        if self.source_ip:
            # Ensure IP related to the routing instance
            if self.source_ip not in IPAddress.objects.filter(interface__device_id=self.routing_instance.device.id):
                raise ValidationError("Group IP not associated with Routing Instance")
            # Ensure VRF membership
            if self.source_ip.vrf != self.vrf:
                raise ValidationError(
                    f"VRF mismatch between PeerGroup VRF ({self.vrf}) and selected source IP VRF ({self.source_ip.vrf})"
                )

        if self.present_in_database:
            original = self.__class__.objects.get(id=self.id)
            if self.vrf != original.vrf and self.endpoints.exists():
                raise ValidationError("Cannot change VRF of PeerGroup that has existing PeerEndpoints in this VRF.")

    def validate_unique(self, exclude=None):
        """Validate uniqueness, handling NULL != NULL for VRF foreign key."""
        if (
            self.vrf is None
            and self.__class__.objects.exclude(id=self.id)
            .filter(routing_instance=self.routing_instance, name=self.name, vrf__isnull=True)
            .exists()
        ):
            raise ValidationError(f"Duplicate Peer Group name for {self.routing_instance}")

        super().validate_unique(exclude)


@extras_features(
    "custom_fields",
    "custom_links",
    "custom_validators",
    "export_templates",
    "graphql",
    "relationships",
    "webhooks",
)
class PeerEndpoint(PrimaryModel, InheritanceMixin, BGPExtraAttributesMixin):
    """BGP information about single endpoint of a peering."""

    extra_attributes_inheritance = ["peer_group", "peer_group.peergroup_template", "routing_instance"]
    property_inheritance = {
        "autonomous_system": ["peer_group", "peer_group.peergroup_template", "routing_instance"],
        "description": ["peer_group", "peer_group.peergroup_template"],
        "enabled": ["peer_group", "peer_group.peergroup_template"],
        "source_ip": ["peer_group"],
        "source_interface": ["peer_group"],
        "role": ["peer_group.role", "peer_group.peergroup_template.role"],
    }

    description = models.CharField(max_length=200, blank=True)

    role = models.ForeignKey(to=PeeringRole, on_delete=models.PROTECT, related_name="endpoints", blank=True, null=True)

    enabled = models.BooleanField(default=True)

    routing_instance = models.ForeignKey(
        to=BGPRoutingInstance,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="endpoints",
        verbose_name="BGP Routing Instance",
    )

    autonomous_system = models.ForeignKey(
        to=AutonomousSystem,
        blank=True,
        null=True,
        related_name="endpoints",
        on_delete=models.PROTECT,
    )

    peer = models.ForeignKey(
        to="self",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    peering = models.ForeignKey(
        to="Peering",
        on_delete=models.CASCADE,
        related_name="endpoints",
    )

    peer_group = models.ForeignKey(
        to=PeerGroup,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="endpoints",
    )

    source_ip = models.ForeignKey(  # local-address
        to="ipam.IPAddress",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="bgp_peer_endpoints",
        verbose_name="BGP Peer IP",
    )

    source_interface = models.ForeignKey(  # update source
        to="dcim.Interface",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="bgp_peer_endpoints",
        verbose_name="Source Interface",
    )

    csv_headers = [
        "routing_instance",
        "peer",
    ]

    def to_csv(self):
        """Export data."""
        return (
            self.routing_instance,
            self.peer,
        )

    @property
    def local_ip(self):
        """Compute effective peering endpoint IP address.

        Peering endpoint IP address value can be sourced from:
         1. Endpoint's `source_ip` attribute
         2. Peer Groups' `source_ip` attribute
         3. Endpoint's `source_interface` attribute
         4. Peer Groups' `source_interface` attribute

        The effective IP Address of an endpoint is based on the above order.
        """
        inherited_source_ip, _, _ = self.get_inherited_field(field_name="source_ip")
        inherited_source_interface, _, _ = self.get_inherited_field(field_name="source_interface")

        if inherited_source_ip:
            return inherited_source_ip

        if inherited_source_interface and inherited_source_interface.ip_addresses.count() == 1:
            return inherited_source_interface.ip_addresses.first()

        return None

    secret = models.ForeignKey(
        to="extras.Secret",
        on_delete=models.PROTECT,
        related_name="bgp_peer_endpoints",
        blank=True,
        null=True,
    )

    def __str__(self):
        """String."""
        asn, _, _ = self.get_inherited_field(field_name="autonomous_system")
        if self.routing_instance and self.routing_instance.device:
            return f"{self.routing_instance.device} {self.local_ip} ({asn})"

        return f"{self.local_ip} ({asn})"

    def get_absolute_url(self):
        """Get the URL for detailed view of a single PeerEndpoint."""
        return reverse("plugins:nautobot_bgp_models:peerendpoint", args=[self.pk])

    def clean(self):
        """
        Clean Method.

        TODO(mzb):
         - add validation on PeerGroup while removing self.ipaddress -> check related Endpoints.
         - ensure self.peering has no more than > endpoints !.
        """
        # Ensure ASN
        asn_value, _, _ = self.get_inherited_field(field_name="autonomous_system")
        if not asn_value:
            raise ValidationError(f"ASN not found at any inheritance level for {self}.")

        # Ensure IP & Update source mutually exclusive:
        if self.source_ip and self.source_interface:
            raise ValidationError("Can not set both IP and Update source options")

        # Ensure source_interface interface has 1 IP Address assigned
        if self.source_interface and self.source_interface.ip_addresses.count() != 1:
            raise ValidationError("Source Interface must have only 1 IP Address assigned.")

        # Ensure IP
        local_ip_value = self.local_ip
        if not local_ip_value:
            raise ValidationError("Endpoint IP not found at any inheritance level .")

        # Ensure IP related to the routing instance
        if self.routing_instance:
            if local_ip_value not in IPAddress.objects.filter(interface__device_id=self.routing_instance.device.id):
                raise ValidationError("Peer IP not associated with Routing Instance")
        # Enforce Routing Instance if local IP belongs to the Device
        elif not self.routing_instance and local_ip_value.interface.exists():
            raise ValidationError("Must specify Routing Instance for this IP Address")

        # Enforce peer group VRF membership
        if self.peer_group is not None:
            if local_ip_value.vrf != self.peer_group.vrf:
                raise ValidationError(
                    f"VRF mismatch between {local_ip_value} (VRF {local_ip_value.vrf}) "
                    f"and peer-group {self.peer_group.name} (VRF {self.peer_group.vrf})"
                )


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
class Peering(OrganizationalModel, StatusModel):
    """Linkage between two PeerEndpoint records."""

    class Meta:
        verbose_name = "BGP Peering"

    @property
    def endpoint_a(self):
        """Get the "first" endpoint associated with this Peering."""
        return self.endpoints.all()[0] if self.endpoints.exists() else None

    @property
    def endpoint_z(self):
        """Get the "second" endpoint associated with this Peering."""
        return self.endpoints.all()[1] if self.endpoints.count() > 1 else None

    def __str__(self):
        """String representation of a single Peering."""
        return f"{self.endpoint_a} ↔︎ {self.endpoint_z}"

    def get_absolute_url(self):
        """Get the URL for a detailed view of a single Peering."""
        return reverse("plugins:nautobot_bgp_models:peering", args=[self.pk])

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

    def validate_peers(self):
        """Peer Sanity Checks."""
        if self.endpoint_a.routing_instance and self.endpoint_a.routing_instance == self.endpoint_z.routing_instance:
            raise ValidationError("Peering between same routing instance not allowed")

        if self.endpoint_a.local_ip == self.endpoint_z.local_ip:
            raise ValidationError("Peering between same IPs not allowed")


@extras_features(
    "custom_fields",
    "custom_links",
    "custom_validators",
    "export_templates",
    "graphql",
    "relationships",
    "webhooks",
)
class AddressFamily(OrganizationalModel, BGPExtraAttributesMixin):
    """Address-family (AFI-SAFI) model for the RoutingInstance and VRF levels of configuration."""

    extra_attributes_inheritance = []

    afi_safi = models.CharField(max_length=64, choices=AFISAFIChoices, verbose_name="AFI-SAFI")

    vrf = models.ForeignKey(
        to="ipam.VRF",
        verbose_name="VRF",
        related_name="address_families",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
    )

    routing_instance = models.ForeignKey(
        to=BGPRoutingInstance,
        on_delete=models.CASCADE,
        related_name="address_families",
        verbose_name="BGP Routing Instance",
    )

    class Meta:
        ordering = ["-routing_instance", "-vrf"]
        verbose_name = "BGP address family"
        verbose_name_plural = "BGP Address Families"

    csv_headers = [
        "routing_instance",
        "vrf",
        "afi_safi",
    ]

    def to_csv(self):
        """Export data."""
        return (
            self.routing_instance.pk,
            self.vrf.name if self.vrf else None,
            self.afi_safi,
        )

    def __str__(self):
        """String representation of a single AddressFamily."""
        if self.vrf:
            return f"{self.afi_safi} AF (VRF {self.vrf}) {self.routing_instance.device}"

        return f"{self.afi_safi} AF - {self.routing_instance.device}"

    def get_absolute_url(self):
        """Get the URL for a detailed view of a single AddressFamily."""
        return reverse("plugins:nautobot_bgp_models:addressfamily", args=[self.pk])

    def validate_unique(self, exclude=None):
        """Validate uniqueness."""
        if (
            not self.vrf
            and self.__class__.objects.exclude(id=self.id)
            .filter(routing_instance=self.routing_instance, afi_safi=self.afi_safi, vrf__isnull=True)
            .exists()
        ):
            raise ValidationError("Duplicate Address Family")

        if (
            self.vrf
            and self.__class__.objects.exclude(id=self.id)
            .filter(routing_instance=self.routing_instance, afi_safi=self.afi_safi, vrf=self.vrf)
            .exists()
        ):
            raise ValidationError("Duplicate Address Family")

        super().validate_unique(exclude)


@extras_features(
    "custom_fields",
    "custom_links",
    "custom_validators",
    "export_templates",
    "graphql",
    "relationships",
    "webhooks",
)
class PeerGroupAddressFamily(OrganizationalModel, InheritanceMixin, BGPExtraAttributesMixin):
    """Address-family (AFI-SAFI) model for PeerGroup-specific configuration."""

    @property
    def get_extra_attributes_paths(self):
        """
        Get inheritable extra attributes.

        Custom implementation as BGPExtraAttributesMixin.get_extra_attributes_paths isn't smart enough.
        """
        try:
            parent_bgp_af = self.peer_group.routing_instance.address_families.get(
                vrf=self.peer_group.vrf, afi_safi=self.afi_safi
            )
            return [parent_bgp_af.extra_attributes]
        except AddressFamily.DoesNotExist:
            return []

    property_inheritance = {}  # no non-extra-attributes properties inherited from AddressFamily at this time

    def get_inherited_field(self, field_name, inheritance_path=None):
        """Returns (value, inheritance_indicator, inheritance_source)."""
        field_value = getattr(self, field_name, None)
        if field_value:
            return field_value, False, None

        try:
            parent_bgp_af = self.peer_group.routing_instance.address_families.get(
                vrf=self.peer_group.vrf, afi_safi=self.afi_safi
            )
            field_value = getattr(parent_bgp_af, field_name, None)
            if field_value:
                return field_value, True, parent_bgp_af
        except AddressFamily.DoesNotExist:
            pass

        return None, False, None

    afi_safi = models.CharField(max_length=64, choices=AFISAFIChoices, verbose_name="AFI-SAFI")

    peer_group = models.ForeignKey(
        to=PeerGroup,
        on_delete=models.CASCADE,
        related_name="address_families",
    )

    import_policy = models.CharField(max_length=100, default="", blank=True)

    export_policy = models.CharField(max_length=100, default="", blank=True)

    multipath = models.BooleanField(blank=True, null=True)

    class Meta:
        ordering = ["-peer_group"]
        unique_together = ["peer_group", "afi_safi"]
        verbose_name = "BGP peer-group address family"
        verbose_name_plural = "BGP Peer-Group Address Families"

    csv_headers = [
        "peer_group",
        "afi_safi",
        "import_policy",
        "export_policy",
        "multipath",
    ]

    def to_csv(self):
        """Return a list of values for use in CSV export."""
        return (
            str(self.peer_group),
            self.afi_safi,
            self.import_policy,
            self.export_policy,
            str(self.multipath),
        )

    def __str__(self):
        """String representation."""
        return f"{self.afi_safi} AF - {self.peer_group}"

    def get_absolute_url(self):
        """Absolute URL of a record."""
        return reverse("plugins:nautobot_bgp_models:peergroupaddressfamily", args=[self.pk])


@extras_features(
    "custom_fields",
    "custom_links",
    "custom_validators",
    "export_templates",
    "graphql",
    "relationships",
    "webhooks",
)
class PeerEndpointAddressFamily(OrganizationalModel, InheritanceMixin, BGPExtraAttributesMixin):
    """Address-family (AFI-SAFI) model for PeerEndpoint-specific configuration."""

    @property
    def get_extra_attributes_paths(self):
        """
        Get inheritable extra attributes.

        Custom implementation as BGPExtraAttributesMixin.get_extra_attributes_paths isn't smart enough.
        """
        inherited_extra_attributes = []

        try:
            parent_pg = self.peer_endpoint.peer_group
            if parent_pg is not None:
                inherited_extra_attributes.append(
                    parent_pg.address_families.get(afi_safi=self.afi_safi).extra_attributes
                )
        except PeerGroupAddressFamily.DoesNotExist:
            pass

        try:
            parent_bgp_af = self.peer_endpoint.routing_instance.address_families.get(
                vrf=self.peer_endpoint.local_ip.vrf, afi_safi=self.afi_safi
            )
            inherited_extra_attributes.append(parent_bgp_af.extra_attributes)
        except AddressFamily.DoesNotExist:
            pass

        return inherited_extra_attributes

    property_inheritance = {
        # Note that only the keys here are actually relevant, as we have a custom get_inherited_field() that ignores
        # the inheritance_path arrays.
        "import_policy": ["peer_group__address_families"],
        "export_policy": ["peer_group__address_families"],
        "multipath": ["peer_group__address_families"],
    }

    def get_inherited_field(self, field_name, inheritance_path=None):
        """Returns (value, inheritance_indicator, inheritance_source)."""
        field_value = getattr(self, field_name, None)
        if field_value:
            return field_value, False, None

        try:
            parent_pg = self.peer_endpoint.peer_group
            if parent_pg is not None:
                parent_pg_af = parent_pg.address_families.get(afi_safi=self.afi_safi)
                field_value = getattr(parent_pg_af, field_name, None)
                if field_value:
                    return field_value, True, parent_pg_af
        except PeerGroupAddressFamily.DoesNotExist:
            pass

        try:
            parent_bgp_af = self.peer_endpoint.routing_instance.address_families.get(
                vrf=self.peer_endpoint.local_ip.vrf, afi_safi=self.afi_safi
            )
            field_value = getattr(parent_bgp_af, field_name, None)
            if field_value:
                return field_value, True, parent_bgp_af
        except AddressFamily.DoesNotExist:
            pass

        return None, False, None

    afi_safi = models.CharField(max_length=64, choices=AFISAFIChoices, verbose_name="AFI-SAFI")

    peer_endpoint = models.ForeignKey(
        to=PeerEndpoint,
        on_delete=models.CASCADE,
        related_name="address_families",
    )

    import_policy = models.CharField(max_length=100, default="", blank=True)

    export_policy = models.CharField(max_length=100, default="", blank=True)

    multipath = models.BooleanField(blank=True, null=True)

    class Meta:
        ordering = ["-peer_endpoint"]
        unique_together = ["peer_endpoint", "afi_safi"]
        verbose_name = "BGP peer-endpoint address family"
        verbose_name_plural = "BGP Peer-Endpoint Address Families"

    csv_headers = [
        "peer_endpoint",
        "afi_safi",
        "import_policy",
        "export_policy",
        "multipath",
    ]

    def to_csv(self):
        """Return a list of values for use in CSV export."""
        return (
            str(self.peer_endpoint),
            self.afi_safi,
            self.import_policy,
            self.export_policy,
            str(self.multipath),
        )

    def __str__(self):
        """String representation."""
        return f"{self.afi_safi} AF - {self.peer_endpoint}"

    def get_absolute_url(self):
        """Absolute URL of a record."""
        return reverse("plugins:nautobot_bgp_models:peerendpointaddressfamily", args=[self.pk])
