"""Generate test data for the BGP Models app."""

import random
from itertools import product

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.db import DEFAULT_DB_ALIAS
from nautobot.circuits.models import Provider
from nautobot.core.factory import get_random_instances
from nautobot.dcim.models import Device, Interface
from nautobot.extras.models import Role, Secret, Status
from nautobot.ipam.models import VRF, IPAddress
from nautobot.tenancy.models import Tenant

from nautobot_bgp_models.choices import AFISAFIChoices
from nautobot_bgp_models.models import (
    AddressFamily,
    AutonomousSystem,
    AutonomousSystemRange,
    BGPRoutingInstance,
    PeerEndpoint,
    PeerEndpointAddressFamily,
    PeerGroup,
    PeerGroupAddressFamily,
    PeerGroupTemplate,
    Peering,
)


class Command(BaseCommand):
    """Populate the database with various data as a baseline for testing (automated or manual)."""

    help = __doc__

    def add_arguments(self, parser):  # noqa: D102
        parser.add_argument(
            "--database",
            default=DEFAULT_DB_ALIAS,
            help='The database to generate the test data in. Defaults to the "default" database.',
        )
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Flush any existing bgp models data from the database before generating new data.",
        )

    def _generate_static_data(self, db):
        providers = get_random_instances(
            Provider.objects.using(db).all(),
            minimum=2,
            maximum=4,
        )
        devices = get_random_instances(
            Device.objects.using(db).all(),
            minimum=2,
            maximum=4,
        )
        ip_addresses = get_random_instances(
            IPAddress.objects.using(db).all(),
            minimum=2,
            maximum=4,
        )
        tenants = get_random_instances(
            Tenant.objects.using(db).all(),
            minimum=2,
            maximum=4,
        )
        roles = get_random_instances(
            Role.objects.using(db).all(),
            minimum=2,
            maximum=4,
        )
        secrets = get_random_instances(
            Secret.objects.using(db).all(),
            minimum=2,
            maximum=4,
        )
        vrfs = get_random_instances(
            VRF.objects.using(db).all(),
            minimum=2,
            maximum=4,
        )
        interfaces = get_random_instances(
            Interface.objects.using(db).all(),
            minimum=2,
            maximum=4,
        )
        statuses = get_random_instances(
            Status.objects.using(db).all(),
            minimum=2,
            maximum=4,
        )
        for status in statuses:
            status.content_types.add(
                *ContentType.objects.filter(
                    app_label="nautobot_bgp_models", model__in=["autonomoussystem", "bgproutinginstance", "peering"]
                ).values_list("pk", flat=True)
            )
        for role in roles:
            role.content_types.add(
                *ContentType.objects.filter(
                    app_label="nautobot_bgp_models", model__in=["peergrouptemplate", "peergroup", "peerendpoint"]
                )
            )

        if len(devices) == 0:
            raise RuntimeError("No devices were found. At least one device is required.")

        # Create Peerings
        peerings = []
        message = "Creating 8 Peerings..."
        self.stdout.write(message)
        for _ in range(1, 9):
            status = random.choice([*statuses, None])  # noqa: S311
            peerings.append(Peering.objects.using(db).create(status=status))

        # Create AutonomousSystemRanges
        autonomous_system_ranges = []
        message = "Creating 8 AutonomousSystemRanges..."
        self.stdout.write(message)
        for i in range(1, 9):
            asn_min = random.randint(64512, 65533)  # noqa: S311
            asn_max = random.randint(asn_min, 65534)  # noqa: S311
            tenant = random.choice([*tenants, None])  # noqa: S311
            autonomous_system_ranges.append(
                AutonomousSystemRange.objects.using(db).create(
                    name=f"AutonomousSystemRange{i}",
                    asn_min=asn_min,
                    asn_max=asn_max,
                    description=f"Autonomous System Range {asn_min} - {asn_max}",
                    tenant=tenant,
                )
            )

        # Create AutonomousSystems
        autonomous_systems = []
        message = "Creating 8 AutonomousSystems..."
        asns = random.choices(range(64512, 65534), k=8)  # noqa: S311
        self.stdout.write(message)
        for i in range(0, 8):
            provider = random.choice([*providers, None])  # noqa: S311
            status = random.choice([*statuses, None])  # noqa: S311
            autonomous_systems.append(
                AutonomousSystem.objects.using(db).create(
                    asn=asns[i],
                    description=f"Autonomous System {asns[i]}",
                    provider=provider,
                    status=status,
                )
            )

        # Create BGPRoutingInstances
        bgp_routing_instances = []
        message = "Creating 8 BGPRoutingInstances..."
        self.stdout.write(message)
        device_autonomous_system_combinations = random.sample(list(product(autonomous_systems, devices)), k=8)  # noqa: S311
        for i in range(0, 8):
            status = random.choice([*statuses, None])  # noqa: S311
            ip_address = random.choice([*ip_addresses, None])  # noqa: S311
            bgp_routing_instances.append(
                BGPRoutingInstance.objects.using(db).create(
                    description=f"BGP Routing Instance {i+1}",
                    device=device_autonomous_system_combinations[i][1],
                    router_id=ip_address,
                    autonomous_system=device_autonomous_system_combinations[i][0],
                    status=status,
                )
            )

        # Create AddressFamilies
        address_families = []
        message = "Creating 8 AddressFamilies..."
        afi_safi_routing_instance_vrf_combinations = random.sample(
            list(product(AFISAFIChoices.values(), bgp_routing_instances, [*vrfs, None])), k=8
        )
        self.stdout.write(message)
        for i in range(0, 8):
            address_families.append(
                AddressFamily.objects.using(db).create(
                    afi_safi=afi_safi_routing_instance_vrf_combinations[i][0],
                    routing_instance=afi_safi_routing_instance_vrf_combinations[i][1],
                    vrf=afi_safi_routing_instance_vrf_combinations[i][2],
                )
            )

        # Create PeerGroupTemplates
        peer_group_templates = []
        message = "Creating 8 PeerGroupTemplates..."
        self.stdout.write(message)
        for i in range(1, 9):
            role = random.choice([*roles, None])  # noqa: S311
            autonomous_system = random.choice([*autonomous_systems, None])  # noqa: S311
            secret = random.choice([*secrets, None])  # noqa: S311
            peer_group_templates.append(
                PeerGroupTemplate.objects.using(db).create(
                    name=f"PeerGroupTemplate{i}",
                    description=f"Peer Group Template {i}",
                    enabled=random.choice([True, False]),  # noqa: S311
                    role=role,
                    autonomous_system=autonomous_system,
                    secret=secret,
                )
            )

        # Create PeerGroups
        peer_groups = []
        message = "Creating 8 PeerGroups..."
        self.stdout.write(message)
        for i in range(1, 9):
            role = random.choice([*roles, None])  # noqa: S311
            autonomous_system = random.choice([*autonomous_systems, None])  # noqa: S311
            secret = random.choice([*secrets, None])  # noqa: S311
            routing_instance = random.choice(bgp_routing_instances)  # noqa: S311
            peer_group_template = random.choice([*peer_group_templates, None])  # noqa: S311
            peer_groups.append(
                PeerGroup.objects.using(db).create(
                    name=f"PeerGroup{i}",
                    description=f"Peer Group {i}",
                    enabled=random.choice([True, False]),  # noqa: S311
                    role=role,
                    autonomous_system=autonomous_system,
                    secret=secret,
                    routing_instance=routing_instance,
                    peergroup_template=peer_group_template,
                )
            )

        # Create PeerGroupAddressFamilys
        peer_group_address_families = []
        message = "Creating 8 PeerGroupAddressFamilies..."
        self.stdout.write(message)
        afi_safi_peer_group_combinations = random.sample(list(product(AFISAFIChoices.values(), peer_groups)), k=8)
        for i in range(0, 8):
            peer_group_address_families.append(
                PeerGroupAddressFamily.objects.using(db).create(
                    afi_safi=afi_safi_peer_group_combinations[i][0],
                    peer_group=afi_safi_peer_group_combinations[i][1],
                    multipath=random.choice([True, False, None]),  # noqa: S311
                )
            )

        # Create PeerEndpoints
        peer_endpoints = []
        message = "Creating 8 PeerEndpoints..."
        self.stdout.write(message)
        for i in range(1, 9):
            role = random.choice([*roles, None])  # noqa: S311
            routing_instance = random.choice([*bgp_routing_instances, None])  # noqa: S311
            autonomous_system = random.choice([*autonomous_systems, None])  # noqa: S311
            peer = random.choice([*peer_endpoints, None])  # noqa: S311
            peering = random.choice(peerings)  # noqa: S311
            peer_group = random.choice([*peer_groups, None])  # noqa: S311
            ip_address = random.choice([*ip_addresses, None])  # noqa: S311
            interface = random.choice([*interfaces, None])  # noqa: S311
            secret = random.choice([*secrets, None])  # noqa: S311
            peer_endpoints.append(
                PeerEndpoint.objects.using(db).create(
                    description=f"Peer Endpoint {i}",
                    role=role,
                    enabled=random.choice([True, False]),  # noqa: S311
                    routing_instance=routing_instance,
                    autonomous_system=autonomous_system,
                    peer=peer,
                    peering=peering,
                    peer_group=peer_group,
                    source_ip=ip_address,
                    source_interface=interface,
                    secret=secret,
                )
            )

        # Create PeerEndpointAddressFamilys
        peer_endpoint_address_families = []
        message = "Creating 8 PeerEndpointAddressFamilies..."
        self.stdout.write(message)
        afi_safi_peer_endpoint_combinations = random.sample(list(product(AFISAFIChoices.values(), peer_endpoints)), k=8)
        for i in range(0, 8):
            peer_endpoint_address_families.append(
                PeerEndpointAddressFamily.objects.using(db).create(
                    afi_safi=afi_safi_peer_endpoint_combinations[i][0],
                    peer_endpoint=afi_safi_peer_endpoint_combinations[i][1],
                )
            )

    def handle(self, *args, **options):
        """Entry point to the management command."""
        if options["flush"]:
            self.stdout.write(self.style.WARNING("Flushing bgp models objects from the database..."))
            PeerEndpointAddressFamily.objects.using(options["database"]).all().delete()
            PeerEndpoint.objects.using(options["database"]).all().delete()
            PeerGroupAddressFamily.objects.using(options["database"]).all().delete()
            PeerGroup.objects.using(options["database"]).all().delete()
            PeerGroupTemplate.objects.using(options["database"]).all().delete()
            AddressFamily.objects.using(options["database"]).all().delete()
            BGPRoutingInstance.objects.using(options["database"]).all().delete()
            AutonomousSystem.objects.using(options["database"]).all().delete()
            AutonomousSystemRange.objects.using(options["database"]).all().delete()
            Peering.objects.using(options["database"]).all().delete()

        self._generate_static_data(db=options["database"])

        self.stdout.write(self.style.SUCCESS(f"Database {options['database']} populated with app data successfully!"))
