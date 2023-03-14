"""Generate BGP data."""
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.db.models import Q
from ipaddress import IPv4Network
from nautobot.circuits.models import Provider, Circuit
from nautobot.dcim.models import Cable, Device, Site, Interface
from nautobot.extras.choices import RelationshipTypeChoices
from nautobot.extras.models import Status, Relationship, RelationshipAssociation, Role
from nautobot.ipam.models import Prefix, IPAddress
from nautobot_bgp_models.models import (
    AutonomousSystem,
    BGPRoutingInstance,
    PeerEndpoint,
    Peering,
    PeerGroup,
    PeerGroupTemplate,
)

PUBLIC_ASN = 65535
PRIVATE_ASN = 4200000000

LOOPBACK_NAME = "Loopback0"

CIRCUIT_SUBNET = "104.94.128.0/18"
CIRCUIT_SUBNET_SIZE = 29
CIRCUIT_SUBNETS_ITER = IPv4Network(str(CIRCUIT_SUBNET)).subnets(new_prefix=CIRCUIT_SUBNET_SIZE)

STATUSES = [
    {"model": AutonomousSystem, "default": ["active", "available", "planned", "failed"]},
    {
        "model": Peering,
        "default": ["active", "decommissioned", "deprovisioning", "offline", "planned", "provisioning"],
    },
]

RELATIONSHIPS = [
    {
        "name": "Site Autonomous System",
        "slug": "site_asn",
        "type": RelationshipTypeChoices.TYPE_ONE_TO_MANY,
        "source_type": ContentType.objects.get_for_model(AutonomousSystem),
        "source_label": "Sites",
        "destination_type": ContentType.objects.get_for_model(Site),
        "destination_label": "Autonomous System",
    },
    {
        "name": "Prefix per Circuit",
        "slug": "prefix_circuit",
        "type": RelationshipTypeChoices.TYPE_ONE_TO_ONE,
        "source_type": ContentType.objects.get_for_model(Circuit),
        # "source_label": "Sites",
        "destination_type": ContentType.objects.get_for_model(Prefix),
        # "destination_label": "Autonomous System",
    },
]

PEERING_ROLES = [
    {
        "name": "Provider",
        "slug": "provider",
        "color": "00bcd4",
    },
    {
        "name": "Customer",
        "slug": "customer",
        "color": "4caf50",
    },
    {
        "name": "Peer",
        "slug": "peer",
        "color": "deafcc",
    },
    {
        "name": "RS",
        "slug": "rs",
        "color": "3f55cc",
    },
    {
        "name": "RS-Client",
        "slug": "rs-client",
        "color": "d11c4f",
    },
]

PEER_GROUP_TEMPLATES = [
    {
        "name": "EDGE-to-LEAF",
        "description": "Global Peer Group for Leafs on Edges",
        "role__slug": "peer",
        "import_policy": "BGP-LEAF-IN",
        "export_policy": "BGP-LEAF-OUT",
    },
    {
        "name": "LEAF-to-EDGE",
        "description": "Peer Group for Edges on Leafs",
        "role__slug": "peer",
        "import_policy": "BGP-EDGE-IN",
        "export_policy": "BGP-EDGE-OUT",
    },
    {
        "name": "EDGE-to-TRANSIT",
        "description": "Peer Group for Transit Providers on Edges",
        "role__slug": "customer",
        "import_policy": "BGP-TRANSIT-IN",
        "export_policy": "BGP-TRANSIT-OUT",
    },
]

EDGE_PEER_GROUPS = [
    {
        "name": "EDGE-to-LEAF",
        "template__name": "EDGE-to-LEAF",
    },
    {
        "name": "EDGE-to-TRANSIT",
        "template__name": "EDGE-to-TRANSIT",
    },
]

LEAF_PEER_GROUPS = [
    {
        "name": "LEAF-to-EDGE",
        "template__name": "LEAF-to-EDGE",
    },
]


def get_cables_by_remote_role(local_role, remote_role):
    """Get cables by endpoints roles."""
    cables = Cable.objects.filter(
        Q(
            _termination_a_device__role__slug=local_role,
            _termination_b_device__role__slug=remote_role,
        )
        | Q(
            _termination_b_device__role__slug=local_role,
            _termination_a_device__role__slug=remote_role,
        )
    )
    return cables


def create_relationship():
    """Create Additional Relationships."""
    for relationship_dict in RELATIONSHIPS:
        Relationship.objects.get_or_create(name=relationship_dict["name"], defaults=relationship_dict)


def create_peering_role():
    """Create peering roles."""
    for peering_role_dict in PEERING_ROLES:
        role, _ = Role.objects.get_or_create(slug=peering_role_dict["slug"], defaults=peering_role_dict)
        role.content_types.add(ContentType.objects.get_for_model(PeerGroup))
        role.content_types.add(ContentType.objects.get_for_model(PeerGroupTemplate))
        role.content_types.add(ContentType.objects.get_for_model(PeerEndpoint))


def create_peer_group_template():
    """Create peer group templates."""
    for pgt in PEER_GROUP_TEMPLATES:
        PeerGroupTemplate.objects.get_or_create(
            name=pgt["name"],
            description=pgt["description"],
            role=Role.objects.get(slug=pgt["role__slug"]),
            import_policy=pgt["import_policy"],
            export_policy=pgt["export_policy"],
        )


def get_next_private_asn(description=None):
    """Get next available asn."""
    next_asn = PRIVATE_ASN
    while True:
        try:
            asn = AutonomousSystem.objects.get(asn=next_asn)
        except AutonomousSystem.DoesNotExist:
            active_status = Status.objects.get_for_model(AutonomousSystem).get(slug="active")
            asn = AutonomousSystem(asn=next_asn, status=active_status, description=description)
            asn.validated_save()
            return asn

        next_asn += 1


def get_next_circuit_prefix():
    """Get next circuit prefix."""
    rel_prefix_circuit = Relationship.objects.get(slug="prefix_circuit")
    while True:
        next_prefix = str(next(CIRCUIT_SUBNETS_ITER))
        try:
            prefix = Prefix.objects.get(prefix=next_prefix)

            # Check if the prefix is already associated with a circuit, if not it's available
            try:
                RelationshipAssociation.objects.get(relationship=rel_prefix_circuit, destination_id=prefix.id)
            except RelationshipAssociation.DoesNotExist:
                return prefix

        except Prefix.DoesNotExist:
            active_status = Status.objects.get_for_model(Prefix).get(slug="active")
            prefix = Prefix(prefix=next_prefix, status=active_status)
            prefix.validated_save()
            return prefix


def get_or_create_relationship(relationship, source, destination):
    """Get an existing relationship or create a new one.

    This function exist by default but somehow it wasn't working properly so I had to create it myself.
    Mainly it was about breaking down source and destination into XXX_id and XXX_type

    Args:
        relationship (Relationship):
        source: Instance of an object compatible with Relationship
        destination ([type]): Instance of an object compatible with Relationship

    Returns:
        (RelationshipAssociation, Boolean) Existing or new created RelationshipAssociation and a flag to indicate if the RA was just created
    """
    ct_source = ContentType.objects.get_for_model(source)
    ct_dest = ContentType.objects.get_for_model(destination)

    try:
        ra = RelationshipAssociation.objects.get(
            relationship=relationship,
            source_type=ct_source,
            source_id=source.id,
            destination_type=ct_dest,
            destination_id=destination.id,
        )
        return ra, False

    except RelationshipAssociation.DoesNotExist:
        ra = RelationshipAssociation(
            relationship=relationship,
            source_type=ct_source,
            source_id=source.id,
            destination_type=ct_dest,
            destination_id=destination.id,
        )
        ra.validated_save()
        return ra, True


class Command(BaseCommand):
    """Command to generate BGP specific data."""

    help = "Generate BGP Data."

    def handle(self, *args, **kwargs):
        """Execute command to generate BGP Data."""
        self.stdout.write("Assigning Default Values ")
        create_relationship()
        create_peering_role()
        create_peer_group_template()

        active_status = Status.objects.get_for_model(AutonomousSystem).get(slug="active")
        active_peering_status = Status.objects.get_for_model(Peering).get(slug="active")

        # ---------------------------------------------
        # Create ASN for all providers
        # ---------------------------------------------

        self.stdout.write("Creating BGP Autonomous Systems")

        for provider in Provider.objects.all():
            if not provider.asn:
                continue

            try:
                _ = AutonomousSystem.objects.get(asn=provider.asn)
            except AutonomousSystem.DoesNotExist:
                AutonomousSystem.objects.create(
                    asn=provider.asn,
                    status=active_status,
                    description=f"ASN for {provider}",
                    provider=provider,
                )

        self.stdout.write("Creating BGP Data")

        # ---------------------------------------------
        # Create ASN and Assign Router ID for all devices
        # ---------------------------------------------
        rel_site = Relationship.objects.get(slug="site_asn")
        rel_prefix_circuit = Relationship.objects.get(slug="prefix_circuit")

        ct_site = ContentType.objects.get_for_model(Site)
        ct_asn = ContentType.objects.get_for_model(AutonomousSystem)

        # For all edge devices, assign the same public ASN
        public_asn, _ = AutonomousSystem.objects.get_or_create(
            asn=PUBLIC_ASN, status=active_status, description="Public ASN for Nautobot Airports"
        )

        # Create Routing Instances
        for edge in Device.objects.filter(
            role__slug="edge",
        ):
            try:
                lo0 = Interface.objects.get(name=LOOPBACK_NAME, device=edge)
                router_id = lo0.ip_addresses.first()

                ri, _ = BGPRoutingInstance.objects.get_or_create(
                    device=edge,
                    description=f"BGP Routing Instance for {edge}",
                    router_id=router_id,
                    autonomous_system=public_asn,
                )

                for pg in EDGE_PEER_GROUPS:
                    PeerGroup.objects.get_or_create(
                        name=pg["name"],
                        template=PeerGroupTemplate.objects.get(name=pg["template__name"]),
                        routing_instance=ri,
                    )

            except Interface.DoesNotExist:
                self.stdout.write(f"Unable to identify the Loopback for {edge.name} .. SKIPPING")
                continue

        # For all Leaf devices, Assign one ASN per Site and assign it to all leaf devices
        for site in Site.objects.filter(tenant__slug="nautobot-airports"):
            # Check if there is already an ASN associated with this site, if not create one
            site_asn = None
            try:
                ra = RelationshipAssociation.objects.get(
                    relationship=rel_site, destination_type=ct_site, destination_id=site.id
                )
                site_asn = ra.source
            except RelationshipAssociation.DoesNotExist:
                site_asn = get_next_private_asn(description=f"Private ASN for Site {site}")
                rel = RelationshipAssociation(
                    relationship=rel_site,
                    source_type=ct_asn,
                    source_id=site_asn.id,
                    destination_type=ct_site,
                    destination_id=site.id,
                )
                rel.validated_save()

            # Associate each leaf devices with the ASN reserved for the site
            for leaf in Device.objects.filter(role__slug="leaf", site=site):
                try:
                    lo0 = Interface.objects.get(name=LOOPBACK_NAME, device=leaf)
                    router_id = lo0.ip_addresses.first()

                    ri, _ = BGPRoutingInstance.objects.get_or_create(
                        device=leaf,
                        description=f"BGP Routing Instance for {leaf}",
                        router_id=router_id,
                        autonomous_system=site_asn,
                    )

                    for pg in LEAF_PEER_GROUPS:
                        PeerGroup.objects.get_or_create(
                            name=pg["name"],
                            template=PeerGroupTemplate.objects.get(name=pg["template__name"]),
                            routing_instance=ri,
                        )

                except Interface.DoesNotExist:
                    self.stdout.write(f"Unable to identify the Loopback for {leaf.name} .. SKIPPING")
                    continue

        # Create Edge<>Leaf peerings:
        edge_leaf_connections = get_cables_by_remote_role("edge", "leaf")

        for edge_leaf_connection in edge_leaf_connections:
            edge_interface = (
                edge_leaf_connection.termination_a
                if edge_leaf_connection.termination_a.parent.role.slug == "edge"
                else edge_leaf_connection.termination_b
            )
            leaf_interface = (
                edge_leaf_connection.termination_a
                if edge_leaf_connection.termination_a.parent.role.slug == "leaf"
                else edge_leaf_connection.termination_b
            )

            if (not edge_interface.parent.tenant.slug == "nautobot-airports") or (
                not edge_interface.parent.tenant.slug == "nautobot-airports"
            ):
                continue

            edge_ip = edge_interface.ip_addresses.first()
            leaf_ip = leaf_interface.ip_addresses.first()

            if not edge_ip or not leaf_ip:
                continue

            edge_device = edge_interface.parent
            leaf_device = leaf_interface.parent

            edge_ri = BGPRoutingInstance.objects.get(device=edge_device)
            leaf_ri = BGPRoutingInstance.objects.get(device=leaf_device)

            peering = Peering.objects.create(status=active_peering_status)

            pe1 = PeerEndpoint.objects.create(
                source_ip=edge_ip,
                peering=peering,
                routing_instance=edge_ri,
                peer_group=PeerGroup.objects.get(
                    name="EDGE-to-LEAF",
                    routing_instance=edge_ri,
                ),
            )
            pe2 = PeerEndpoint.objects.create(
                source_ip=leaf_ip,
                peering=peering,
                routing_instance=leaf_ri,
                peer_group=PeerGroup.objects.get(
                    name="LEAF-to-EDGE",
                    routing_instance=leaf_ri,
                ),
            )

            peering.update_peers()

        # Create peering with Transit Providers on Edges (for every circuit connected on an edge)
        for edge in Device.objects.filter(role__slug="edge"):
            for intf in Interface.objects.filter(device=edge, _custom_field_data__role="external"):
                if not intf.connected_endpoint or not hasattr(intf.connected_endpoint, "circuit"):
                    continue

                circuit = intf.connected_endpoint.circuit
                provider_asn = AutonomousSystem.objects.filter(provider=circuit.provider).first()

                if not provider_asn:
                    continue

                # Check if there is already a prefix associated with this circuit, it not, allocate one and assign it
                try:
                    rel = RelationshipAssociation.objects.get(relationship=rel_prefix_circuit, source_id=circuit.id)
                    prefix = rel.destination
                except RelationshipAssociation.DoesNotExist:
                    prefix = get_next_circuit_prefix()
                    rel = RelationshipAssociation(relationship=rel_prefix_circuit, source=circuit, destination=prefix)
                    rel.validated_save()

                # Create 2 IP Addresses based on the prefix associated with the circuit
                edge_ip, _ = IPAddress.objects.get_or_create(
                    address=prefix.get_first_available_ip(), status=active_status
                )
                edge_ip.assigned_object = intf
                edge_ip.validated_save()

                circuit_ip, _ = IPAddress.objects.get_or_create(
                    address=prefix.get_first_available_ip(), status=active_status
                )

                # Get Routing Instance
                edge_device = intf.parent
                edge_ri = BGPRoutingInstance.objects.get(device=edge_device)

                # Create the BGP peering
                peering = Peering.objects.create(status=active_peering_status)
                peering.validated_save()

                pe1 = PeerEndpoint.objects.create(
                    source_ip=edge_ip,
                    peering=peering,
                    routing_instance=edge_ri,
                    peer_group=PeerGroup.objects.get(
                        name="EDGE-to-TRANSIT",
                        routing_instance=edge_ri,
                    ),
                )
                pe1.validated_save()

                pe2 = PeerEndpoint.objects.create(
                    source_ip=circuit_ip,
                    autonomous_system=provider_asn,
                    peering=peering,
                )
                pe2.validated_save()

                peering.update_peers()
