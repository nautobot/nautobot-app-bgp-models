"""Django model definitions for nautobot_bgp_models."""

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
from django.urls import reverse

from nautobot.core.models.generics import PrimaryModel, OrganizationalModel
from nautobot.dcim.fields import ASNField
from nautobot.dcim.models import Device
from nautobot.extras.models import Relationship, RelationshipAssociation, StatusModel
from nautobot.extras.utils import extras_features
from nautobot.utilities.choices import ColorChoices
from nautobot.utilities.fields import ColorField

from . import choices


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
    "webhooks",
)
class PeeringRole(OrganizationalModel):
    """Role definition for use with a PeerGroup or PeerEndpoint."""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    color = ColorField(default=ColorChoices.COLOR_GREY)
    description = models.CharField(max_length=200, blank=True)

    csv_headers = ["name", "slug", "color", "description"]

    class Meta:
        verbose_name = "BGP peering role"

    def __str__(self):
        """String representation of a PeeringRole."""
        return self.name

    def get_absolute_url(self):
        """Get the URL for a detailed view of a single PeeringRole."""
        return reverse("plugins:nautobot_bgp_models:peeringrole", args=[self.pk])

    def to_csv(self):
        """Render a PeeringRole record to CSV fields."""
        return (self.name, self.slug, self.color, self.description)


class AbstractPeeringInfo(models.Model):
    """Abstract base class shared by PeerGroup and PeeringEndpoint models."""

    description = models.CharField(max_length=200, blank=True)
    enabled = models.BooleanField(default=True)

    vrf = models.ForeignKey(
        to="ipam.VRF",
        verbose_name="VRF",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
    )

    update_source_content_type = models.ForeignKey(
        to=ContentType,
        limit_choices_to=models.Q(
            models.Q(app_label="dcim", model="interface") | models.Q(app_label="virtualization", model="vminterface")
        ),
        on_delete=models.CASCADE,
        related_name="+",
        blank=True,
        null=True,
    )
    update_source_object_id = models.UUIDField(blank=True, null=True)
    update_source = GenericForeignKey(ct_field="update_source_content_type", fk_field="update_source_object_id")

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

    maximum_paths_ibgp = models.IntegerField(blank=True, null=True, verbose_name="maximum-paths (iBGP)")
    maximum_paths_ebgp = models.IntegerField(blank=True, null=True, verbose_name="maximum-paths (eBGP)")
    maximum_paths_eibgp = models.IntegerField(blank=True, null=True, verbose_name="maximum-paths (eiBGP)")
    maximum_prefix = models.IntegerField(blank=True, null=True)

    bfd_multiplier = models.IntegerField(blank=True, null=True, verbose_name="BFD multiplier")
    bfd_minimum_interval = models.IntegerField(blank=True, null=True, verbose_name="BFD minimum interval")
    bfd_fast_detection = models.BooleanField(blank=True, null=True, verbose_name="BFD fast-detection")

    enforce_first_as = models.BooleanField(blank=True, null=True)
    send_community_ebgp = models.BooleanField(blank=True, null=True, verbose_name="Send-community eBGP")

    class Meta:
        abstract = True

    def get_candidate_devices(self):
        """Helper function for clean() - various attributes may refer to various Device and/or VirtualMachine."""
        device_candidates = set()

        if self.router_id:
            if self.router_id.assigned_object:
                if hasattr(self.router_id.assigned_object, "device"):
                    device_candidates.add(self.router_id.assigned_object.device)
                else:
                    device_candidates.add(self.router_id.assigned_object.virtual_machine)
            else:
                device_candidates.add(None)

        if self.update_source:
            if hasattr(self.update_source, "device"):
                device_candidates.add(self.update_source.device)
            else:
                device_candidates.add(self.update_source.virtual_machine)

        return device_candidates

    def get_candidate_vrfs(self):
        """Helper function for clean() - various attributes may refer to various VRF records."""
        vrf_candidates = set()
        if self.router_id:
            vrf_candidates.add(self.router_id.vrf)

        return vrf_candidates

    def clean(self):
        """Django callback method to validate model sanity."""
        super().clean()

        device_candidates = self.get_candidate_devices()
        if len(device_candidates) > 1:
            raise ValidationError(
                f"Various attributes refer to different devices and/or virtual machines: {device_candidates}"
            )

        vrf_candidates = self.get_candidate_vrfs()
        if len(vrf_candidates) > 1:
            raise ValidationError(f"Various attributes refer to different VRFs: {vrf_candidates}")
        # If no VRF was specified explicitly but it's implied by other attributes, use that
        if self.vrf is None and len(vrf_candidates) == 1:
            self.vrf = vrf_candidates.pop()
        elif vrf_candidates and self.vrf not in vrf_candidates:
            raise ValidationError(
                f"VRF {self.vrf} was specified, but one or more attributes refer instead to {vrf_candidates.pop()}"
            )

    def get_fields(self, include_inherited=False):  # pylint: disable=unused-argument
        """Get a listing of model fields, optionally including values inherited via the BGP config hierarchy.

        Args:
            include_inherited (bool): If True, for any fields with a local None/null value, check for any
                "upstream" related objects that do define a value for this field and include that inherited value.

        Returns:
            Dict[dict]: one dict per relevant field on this model, with at least the keys
                "value" (field value - integer, string, object reference, etc.), and "inherited" (boolean).
                For properties that are inherited (given include_inherited=True), there will also be a "source" key,
                whose value is the model object that the value is inherited from.


                {
                    "bfd_multiplier": {"value": 10, "inherited": False},
                    "vrf": {"value": <VRF object>, "inherited": False},
                    "router_id": {"value": <IPAddress object>, "inherited": True, "source": <Device object>},
                    ...
                }
        """
        # The base AbstractPeeringInfo model doesn't have anything to inherit properties from
        return {
            "description": {"value": self.description, "inherited": False},
            "enabled": {"value": self.enabled, "inherited": False},
            "vrf": {"value": self.vrf, "inherited": False},
            "update_source": {"value": self.update_source, "inherited": False},
            "router_id": {"value": self.router_id, "inherited": False},
            "autonomous_system": {"value": self.autonomous_system, "inherited": False},
            "maximum_paths_ibgp": {"value": self.maximum_paths_ibgp, "inherited": False},
            "maximum_paths_ebgp": {"value": self.maximum_paths_ebgp, "inherited": False},
            "maximum_paths_eibgp": {"value": self.maximum_paths_eibgp, "inherited": False},
            "maximum_prefix": {"value": self.maximum_prefix, "inherited": False},
            "bfd_multiplier": {"value": self.bfd_multiplier, "inherited": False},
            "bfd_minimum_interval": {"value": self.bfd_minimum_interval, "inherited": False},
            "bfd_fast_detection": {"value": self.bfd_fast_detection, "inherited": False},
            "enforce_first_as": {"value": self.enforce_first_as, "inherited": False},
            "send_community_ebgp": {"value": self.send_community_ebgp, "inherited": False},
        }


@extras_features(
    "custom_fields",
    "custom_links",
    "custom_validators",
    "export_templates",
    "relationships",
    "webhooks",
)
class PeerGroup(AbstractPeeringInfo, OrganizationalModel):
    """BGP peer group information."""

    name = models.CharField(max_length=100)

    role = models.ForeignKey(to=PeeringRole, on_delete=models.PROTECT, related_name="peer_groups")

    class Meta:
        ordering = ["name"]
        verbose_name = "BGP peer group"

    def __str__(self):
        """String representation of a single PeerGroup."""
        return f"{self.name}"

    def get_absolute_url(self):
        """Get the URL for a detailed view of a single PeerGroup."""
        return reverse("plugins:nautobot_bgp_models:peergroup", args=[self.pk])

    def get_fields(self, include_inherited=False):
        """Get a listing of model fields, optionally including values inherited via the BGP config hierarchy."""
        result = super().get_fields(include_inherited=include_inherited)

        # Add additional fields
        result.update(
            {
                "name": {"value": self.name, "inherited": False},
                "role": {"value": self.role, "inherited": False},
            }
        )

        return result


@extras_features(
    "custom_fields",
    "custom_links",
    "custom_validators",
    "export_templates",
    "relationships",
    "webhooks",
)
class PeerEndpoint(AbstractPeeringInfo, PrimaryModel):
    """BGP information about one endpoint of a peering session."""

    peer_group = models.ForeignKey(
        to=PeerGroup,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="peer_endpoints",
    )
    local_ip = models.ForeignKey(
        to="ipam.IPAddress",
        on_delete=models.CASCADE,
        related_name="bgp_peer_endpoints",
        verbose_name="Local IP",
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

    class Meta:
        ordering = ["local_ip"]
        # TODO unique_together?
        verbose_name = "BGP peer endpoint"

    def __str__(self):
        """String representation of a single PeerEndpoint."""
        return f"{self.local_ip} ({self.get_autonomous_system() or 'unknown AS'})"

    def get_absolute_url(self):
        """Get the URL for a detailed view of a single PeerEndpoint."""
        return reverse("plugins:nautobot_bgp_models:peerendpoint", args=[self.pk])

    def clean(self):
        """Model validation logic for PeerEndpoint."""
        if not self.present_in_database and self.session.endpoints.count() >= 2:
            raise ValidationError("The maximum number of PeerEndpoint for this session has been reached already (2).")

        super().clean()

    def get_autonomous_system(self):
        """Get the (possibly inherited) AutonomousSystem for this PeerEndpoint."""
        if self.autonomous_system:
            return self.autonomous_system
        if self.peer_group and self.peer_group.autonomous_system:
            return self.peer_group.autonomous_system
        bgp_asn_relation = Relationship.objects.get(slug="bgp_asn")
        if self.local_ip.assigned_object and hasattr(self.local_ip.assigned_object, "device"):
            try:
                return RelationshipAssociation.objects.get(
                    relationship=bgp_asn_relation,
                    destination_type=ContentType.objects.get_for_model(Device),
                    destination_id=self.local_ip.assigned_object.device.pk,
                ).source
            except ObjectDoesNotExist:
                pass
        return None

    def get_device(self):
        """Get the (derived) Device or VirtualMachine for this PeerEndpoint, if any."""
        if self.local_ip.assigned_object and hasattr(self.local_ip.assigned_object, "device"):
            return self.local_ip.assigned_object.device
        if self.local_ip.assigned_object and hasattr(self.local_ip.assigned_object, "virtualmachine"):
            return self.local_ip.assigned_object.virtualmachine
        return None

    def get_candidate_devices(self):
        """Helper function for clean() - various attributes may refer to various Device and/or VirtualMachine."""
        device_candidates = super().get_candidate_devices()

        if self.local_ip.assigned_object:
            if hasattr(self.local_ip.assigned_object, "device"):
                device_candidates.add(self.local_ip.assigned_object.device)
            else:
                device_candidates.add(self.local_ip.assigned_object.virtual_machine)
        else:
            device_candidates.add(None)

        return device_candidates

    def get_candidate_vrfs(self):
        """Helper function for clean() - various attributes may refer to various VRF records."""
        vrf_candidates = super().get_candidate_vrfs()

        vrf_candidates.add(self.local_ip.vrf)
        if self.peer_group:
            vrf_candidates.add(self.peer_group.vrf)

        return vrf_candidates

    def get_fields(self, include_inherited=False):
        """Get a listing of model fields, optionally including values inherited via the BGP config hierarchy."""
        result = super().get_fields(include_inherited=include_inherited)

        # Add additional fields
        result.update(
            {
                "peer_group": {"value": self.peer_group, "inherited": False},
                "local_ip": {"value": self.local_ip, "inherited": False},
                "peer": {"value": self.peer, "inherited": False},
                "session": {"value": self.session, "inherited": False},
            }
        )

        if include_inherited:
            # Add inherited field values
            if self.peer_group:
                peer_group_result = self.peer_group.get_fields(include_inherited=include_inherited)
                for key in result:
                    if (
                        key in peer_group_result
                        and peer_group_result[key]["value"] is not None
                        and result[key]["value"] is None
                    ):
                        result[key].update(
                            {
                                "value": peer_group_result[key]["value"],
                                # Source is the peer group's source, if any, otherwise the peer group itself
                                "source": peer_group_result[key].get("source", self.peer_group),
                                "inherited": True,
                            }
                        )

            if self.local_ip.assigned_object and hasattr(self.local_ip.assigned_object, "device"):
                device = self.local_ip.assigned_object.device
                # TODO helper function to reduce duplicate code
                if not result["router_id"]["value"]:
                    try:
                        device_router_id_assoc = RelationshipAssociation.objects.get(
                            relationship__slug="bgp_device_router_id",
                            source_type=ContentType.objects.get_for_model(Device),
                            source_id=device.pk,
                        )
                        result["router_id"].update(
                            {
                                "value": device_router_id_assoc.destination,
                                "source": device,
                                "inherited": True,
                            }
                        )
                    except RelationshipAssociation.DoesNotExist:
                        pass

                if not result["autonomous_system"]["value"]:
                    try:
                        asn_device_assoc = RelationshipAssociation.objects.get(
                            relationship__slug="bgp_asn",
                            destination_type=ContentType.objects.get_for_model(Device),
                            destination_id=device.pk,
                        )
                        result["autonomous_system"].update(
                            {
                                "value": asn_device_assoc.source,
                                "source": device,
                                "inherited": True,
                            }
                        )
                    except RelationshipAssociation.DoesNotExist:
                        pass

        return result


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

    role = models.ForeignKey(to=PeeringRole, on_delete=models.PROTECT)

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
class AddressFamily(OrganizationalModel):
    """Address-family (AFI-SAFI) configuration for BGP."""

    afi_safi = models.CharField(max_length=64, choices=choices.AFISAFIChoices, verbose_name="AFI-SAFI")

    peer_group = models.ForeignKey(to=PeerGroup, on_delete=models.CASCADE, blank=True, null=True)
    peer_endpoint = models.ForeignKey(to=PeerEndpoint, on_delete=models.CASCADE, blank=True, null=True)

    import_policy = models.CharField(max_length=100, default="", blank=True)
    export_policy = models.CharField(max_length=100, default="", blank=True)
    redistribute_static_policy = models.CharField(max_length=100, default="", blank=True)

    maximum_prefix = models.IntegerField(blank=True, null=True)
    multipath = models.BooleanField(blank=True, null=True)

    class Meta:
        # We'd like to order by device name but since it's a GenericForeignKey that's not easily possible.
        # The below ordering puts all device-level AFs at the beginning of the list, then all peer-group-specific AFs,
        # and finally all peer-endpoint-specific AFs.
        ordering = ["-peer_endpoint", "-peer_group"]
        unique_together = [("afi_safi", "peer_group", "peer_endpoint")]
        verbose_name = "BGP address-family"
        verbose_name_plural = "BGP address-families"

    def __str__(self):
        """String representation of a single AddressFamily."""
        if self.peer_group:
            return f"AFI-SAFI {self.afi_safi} for {self.peer_group}"
        if self.peer_endpoint:
            return f"AFI-SAFI {self.afi_safi} for {self.peer_endpoint}"
        return f"AFI-SAFI {self.afi_safi}"

    def get_absolute_url(self):
        """Get the URL for a detailed view of a single AddressFamily."""
        return reverse("plugins:nautobot_bgp_models:addressfamily", args=[self.pk])

    def clean(self):
        """Django callback method to validate model sanity."""
        super().clean()

        if self.peer_group and self.peer_endpoint:
            raise ValidationError("An AddressFamily cannot reference both a peer-group and a peer endpoint")

        # Since NULL != NULL in database terms, unique_together as defined on the Meta class above doesn't exactly
        # work as might be expected, given that either peer_group or peer_endpoint (or both!) will be NULL.w
        # We need to enforce the intention of the rule explicitly here:
        if (
            AddressFamily.objects.exclude(pk=self.pk)
            .filter(
                afi_safi=self.afi_safi,
                peer_group=self.peer_group,
                peer_endpoint=self.peer_endpoint,
            )
            .exists()
        ):
            raise ValidationError(
                "AddressFamily is already defined for the given device, AFI/SAFI, and peer-group/peer-endpoint (if any)"
            )

    def get_fields(self, include_inherited=False):
        """Get a listing of model fields, optionally including values inherited via the BGP config hierarchy."""
        result = {
            "import_policy": {"value": self.import_policy, "inherited": False},
            "export_policy": {"value": self.export_policy, "inherited": False},
            "redistribute_static_policy": {"value": self.redistribute_static_policy, "inherited": False},
            "maximum_prefix": {"value": self.maximum_prefix, "inherited": False},
            "multipath": {"value": self.multipath, "inherited": False},
        }
        if include_inherited:
            if self.peer_endpoint and self.peer_endpoint.peer_group:
                # inherit from peer-group address-family, if any
                try:
                    pg_af = self.__class__.objects.get(afi_safi=self.afi_safi, peer_group=self.peer_endpoint.peer_group)
                    pg_af_fields = pg_af.get_fields(include_inherited=include_inherited)
                    for key in result:
                        if (
                            key in pg_af_fields
                            and pg_af_fields[key]["value"] is not None
                            and (result[key]["value"] is None or result[key]["value"] == "")
                        ):
                            result[key].update(
                                {
                                    "value": pg_af_fields[key]["value"],
                                    "source": pg_af_fields[key].get("source", pg_af),
                                    "inherited": True,
                                }
                            )
                except ObjectDoesNotExist:
                    pass

        return result
