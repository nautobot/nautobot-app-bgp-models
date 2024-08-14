"""Unit test automation for FilterSet classes in nautobot_bgp_models."""

from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

# from nautobot.circuits.models import Provider
from nautobot.dcim.choices import InterfaceTypeChoices
from nautobot.dcim.models import Device, DeviceType, Interface, Location, LocationType, Manufacturer
from nautobot.extras.models import Role, Status
from nautobot.ipam.models import IPAddress, Namespace, Prefix

from nautobot_bgp_models import choices, filters, models


class AutonomousSystemTestCase(TestCase):
    """Test filtering of AutonomousSystem records."""

    queryset = models.AutonomousSystem.objects.all()
    filterset = filters.AutonomousSystemFilterSet

    @classmethod
    def setUpTestData(cls):
        """One-time class setup to prepopulate required data for tests."""
        status_active = Status.objects.get(name__iexact="active")
        status_active.content_types.add(ContentType.objects.get_for_model(models.AutonomousSystem))

        cls.status_primary_asn = Status.objects.create(name="Primary ASN", color="FFFFFF")
        cls.status_primary_asn.content_types.add(ContentType.objects.get_for_model(models.AutonomousSystem))

        cls.status_remote_asn = Status.objects.create(name="Remote ASN", color="FFFFFF")
        cls.status_remote_asn.content_types.add(ContentType.objects.get_for_model(models.AutonomousSystem))

        models.AutonomousSystem.objects.create(
            asn=4200000000, status=status_active, description="Reserved for private use"
        )
        models.AutonomousSystem.objects.create(
            asn=4200000001, status=cls.status_primary_asn, description="Also reserved for private use"
        )
        models.AutonomousSystem.objects.create(
            asn=4200000002, status=cls.status_remote_asn, description="Another reserved for private use"
        )

    def test_id(self):
        """Test filtering by ID (primary key)."""
        params = {"id": self.queryset.values_list("pk", flat=True)[:2]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_asn(self):
        """Test filtering by ASN."""
        params = {"asn": [4200000000, 4200000001]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_status(self):
        """Test filtering by status."""
        params = {"status": [self.status_primary_asn.name, self.status_remote_asn.name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class AutonomousSystemRangeTestCase(TestCase):
    """Test filtering of AutonomousSystemRange records."""

    queryset = models.AutonomousSystemRange.objects.all()
    filterset = filters.AutonomousSystemRangeFilterSet

    @classmethod
    def setUpTestData(cls):
        """One-time class setup to prepopulate required data for tests."""
        cls.asn_range_1 = models.AutonomousSystemRange.objects.create(
            name="Public asns", asn_min=100, asn_max=125, description="Test Range 1"
        )

        cls.asn_range_2 = models.AutonomousSystemRange.objects.create(
            name="DC asns", asn_min=1000, asn_max=2000, description="asns for dc"
        )

        cls.asn_range_3 = models.AutonomousSystemRange.objects.create(
            name="DC asns 2", asn_min=2001, asn_max=3000, description="asns for dc"
        )

    def test_id(self):
        """Test filtering by ID."""
        params = {"id": self.queryset.values_list("pk", flat=True)[:2]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_name(self):
        """Test filtering by Name."""
        params = {"name": ["DC asns", "DC asns 2"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_min_max(self):
        """Test filtering by ASN Min."""
        params = {"asn_min": [1000]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"asn_max": [3000]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)


class PeerGroupTestCase(TestCase):
    """Test filtering of PeerGroup records."""

    queryset = models.PeerGroup.objects.all()
    filterset = filters.PeerGroupFilterSet

    @classmethod
    def setUpTestData(cls):
        """One-time class setup."""
        status_active = Status.objects.get(name__iexact="active")
        status_active.content_types.add(ContentType.objects.get_for_model(models.AutonomousSystem))

        manufacturer = Manufacturer.objects.create(name="Cisco")
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model="CSR 1000V")
        location_type = LocationType.objects.create(name="site")
        location_status = Status.objects.get_for_model(Location).first()
        location = Location.objects.create(name="Site 1", location_type=location_type, status=location_status)
        devicerole = Role.objects.create(name="Router", color="ff0000")
        devicerole.content_types.add(ContentType.objects.get_for_model(Device))
        cls.device_1 = Device.objects.create(
            device_type=devicetype, role=devicerole, name="Device 1", location=location, status=status_active
        )
        cls.device_2 = Device.objects.create(
            device_type=devicetype, role=devicerole, name="Device 2", location=location, status=status_active
        )

        cls.asn_1 = models.AutonomousSystem.objects.create(asn=4294967294, status=status_active)
        asn_2 = models.AutonomousSystem.objects.create(asn=4294967295, status=status_active)

        cls.peeringrole_internal = Role.objects.create(name="Internal", color="333333")
        cls.peeringrole_internal.content_types.add(ContentType.objects.get_for_model(models.PeerGroup))
        peeringrole_external = Role.objects.create(name="External", color="ffffff")
        peeringrole_external.content_types.add(ContentType.objects.get_for_model(models.PeerGroup))

        cls.bgp_routing_instance_1 = models.BGPRoutingInstance.objects.create(
            description="Hello World!",
            autonomous_system=cls.asn_1,
            device=cls.device_1,
            status=status_active,
        )
        cls.bgp_routing_instance_2 = models.BGPRoutingInstance.objects.create(
            description="Hello World!",
            autonomous_system=asn_2,
            device=cls.device_2,
            status=status_active,
        )

        models.PeerGroup.objects.create(
            routing_instance=cls.bgp_routing_instance_1,
            name="Group A",
            role=cls.peeringrole_internal,
            autonomous_system=cls.asn_1,
            description="Internal Group",
        )
        models.PeerGroup.objects.create(
            routing_instance=cls.bgp_routing_instance_1,
            name="Group B",
            role=peeringrole_external,
            autonomous_system=cls.asn_1,
            enabled=False,
            description="External Group",
        )
        models.PeerGroup.objects.create(
            routing_instance=cls.bgp_routing_instance_1,
            name="Group C",
            role=cls.peeringrole_internal,
            autonomous_system=asn_2,
            description="Internal Group",
            # vrf=cls.vrf
        )
        models.PeerGroup.objects.create(
            routing_instance=cls.bgp_routing_instance_2,
            name="Group C",
            role=cls.peeringrole_internal,
            autonomous_system=asn_2,
            description="Internal Group",
            # vrf=cls.vrf
        )

    def test_search(self):
        """Test text search."""
        # Match on name (case-insensitive)
        self.assertEqual(self.filterset({"q": "Group A"}, self.queryset).qs.count(), 1)
        self.assertEqual(self.filterset({"q": "group a"}, self.queryset).qs.count(), 1)
        self.assertEqual(self.filterset({"q": "Internal Group"}, self.queryset).qs.count(), 3)
        self.assertEqual(self.filterset({"q": "External Group"}, self.queryset).qs.count(), 1)

    def test_id(self):
        """Test filtering by ID (primary key)."""
        params = {"id": self.queryset.values_list("pk", flat=True)[:2]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_enabled(self):
        """Test filtering by enabled status."""
        params = {"enabled": True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_device(self):
        """Test filtering by device name."""
        params = {"device": [self.device_1.name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_device_id(self):
        """Test filtering by device ID."""
        params = {"device_id": [self.device_1.id]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_role(self):
        """Test filtering by peering role."""
        params = {"role": [self.peeringrole_internal.name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_autonomous_system(self):
        """Test filtering by autonomous system."""
        params = {"autonomous_system": [4294967294]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_routing_instance(self):
        """Test Routing Instance."""
        self.assertEqual(
            self.filterset({"routing_instance": [self.bgp_routing_instance_1.pk]}, self.queryset).qs.count(), 3
        )


class PeerEndpointTestCase(TestCase):
    """Test filtering of PeerEndpoint records."""

    queryset = models.PeerEndpoint.objects.all()
    filterset = filters.PeerEndpointFilterSet

    @classmethod
    def setUpTestData(cls):  # pylint: disable=too-many-locals
        """One-time class setup."""
        status_active = Status.objects.get(name__iexact="active")
        status_active.content_types.add(ContentType.objects.get_for_model(models.AutonomousSystem))

        # provider = Provider.objects.create(name="Provider", slug="provider")

        asn = models.AutonomousSystem.objects.create(asn=4294967295, status=status_active)
        # asn_15521 = models.AutonomousSystem.objects.create(asn=15521, status=status_active, provider=provider)

        peeringrole = Role.objects.create(name="Internal", color="ffffff")
        peeringrole.content_types.add(ContentType.objects.get_for_model(models.PeerGroup))
        manufacturer = Manufacturer.objects.create(name="Cisco")
        cls.devicetype = DeviceType.objects.create(manufacturer=manufacturer, model="CSR 1000V")
        location_type = LocationType.objects.create(name="site")
        location_status = Status.objects.get_for_model(Location).first()
        cls.location = Location.objects.create(name="Site 1", location_type=location_type, status=location_status)
        cls.devicerole = Role.objects.create(name="Router", color="ff0000")
        cls.devicerole.content_types.add(ContentType.objects.get_for_model(Device))
        cls.device = Device.objects.create(
            device_type=cls.devicetype,
            role=cls.devicerole,
            name="Device 1",
            location=cls.location,
            status=status_active,
        )
        interface_status = Status.objects.get_for_model(Interface).first()
        interface = Interface.objects.create(
            device=cls.device, name="Loopback1", type=InterfaceTypeChoices.TYPE_VIRTUAL, status=interface_status
        )

        namespace = Namespace.objects.first()
        prefix_status = Status.objects.get_for_model(Prefix).first()
        Prefix.objects.create(prefix="1.0.0.0/8", namespace=namespace, status=prefix_status)

        addresses = [
            IPAddress.objects.create(address="1.1.1.1/32", status=status_active, namespace=namespace),
            IPAddress.objects.create(address="1.1.1.2/32", status=status_active, namespace=namespace),
            IPAddress.objects.create(address="1.1.1.3/32", status=status_active, namespace=namespace),
        ]

        interface.add_ip_addresses([addresses[0], addresses[1]])

        cls.bgp_routing_instance = models.BGPRoutingInstance.objects.create(
            description="Hello World!",
            autonomous_system=asn,
            device=cls.device,
            status=status_active,
        )

        cls.peergroup = models.PeerGroup.objects.create(
            name="Group B",
            role=peeringrole,
            routing_instance=cls.bgp_routing_instance,
        )

        peering1 = models.Peering.objects.create(status=status_active)
        peering2 = models.Peering.objects.create(status=status_active)
        peering3 = models.Peering.objects.create(status=status_active)

        models.PeerEndpoint.objects.create(
            routing_instance=cls.bgp_routing_instance,
            source_ip=addresses[0],
            autonomous_system=asn,
            peering=peering1,
        )
        models.PeerEndpoint.objects.create(
            routing_instance=cls.bgp_routing_instance,
            source_ip=addresses[1],
            autonomous_system=asn,
            peer_group=cls.peergroup,
            peering=peering2,
        )
        models.PeerEndpoint.objects.create(
            source_ip=addresses[2],
            peer_group=cls.peergroup,
            enabled=False,
            peering=peering3,
        )

    def test_search(self):
        """Test text search."""
        self.assertEqual(self.filterset({"q": "Device 1"}, self.queryset).qs.count(), 2)
        self.assertEqual(self.filterset({"q": "device 1"}, self.queryset).qs.count(), 2)

    def test_id(self):
        """Test filtering by ID (primary key)."""
        params = {"id": self.queryset.values_list("pk", flat=True)[:2]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_enabled(self):
        """Test filtering by enabled status."""
        params = {"enabled": True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_autonomous_system(self):
        """Test filtering by autonomous system."""
        params = {"autonomous_system": [4294967295]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_peer_group(self):
        """Test filtering by peer-group."""
        params = {"peer_group": [self.peergroup.pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_device(self):
        """Test filtering by device name."""
        params = {"device": ["Device 1"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_device_id(self):
        """Test filtering by device ID."""
        params = {"device_id": [self.device.pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class PeeringTestCase(TestCase):
    """Test filtering of Peering records."""

    queryset = models.Peering.objects.all()
    filterset = filters.PeeringFilterSet

    @classmethod
    def setUpTestData(cls):  # pylint: disable=too-many-locals
        """One-time class setup to prepopulate required data for tests."""
        status_active = Status.objects.get(name__iexact="active")
        cls.status_active = status_active
        status_active.content_types.add(ContentType.objects.get_for_model(models.Peering))
        status_active.content_types.add(ContentType.objects.get_for_model(models.AutonomousSystem))

        status_reserved = Status.objects.get(name__iexact="reserved")
        status_reserved.content_types.add(ContentType.objects.get_for_model(models.Peering))

        asn1 = models.AutonomousSystem.objects.create(asn=65000, status=status_active)
        asn2 = models.AutonomousSystem.objects.create(asn=66000, status=status_active)
        asn3 = models.AutonomousSystem.objects.create(asn=12345, status=status_active)

        manufacturer = Manufacturer.objects.create(name="Cisco")
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model="CSR 1000V")
        location_type = LocationType.objects.create(name="site")
        location_status = Status.objects.get_for_model(Location).first()
        location = Location.objects.create(name="Site 1", location_type=location_type, status=location_status)
        devicerole_router = Role.objects.create(name="Router", color="ff0000")
        devicerole_switch = Role.objects.create(name="Switch", color="ff0000")
        cls.device1 = Device.objects.create(
            device_type=devicetype,
            role=devicerole_router,
            name="device1",
            location=location,
            status=status_active,
        )
        cls.device2 = Device.objects.create(
            device_type=devicetype,
            role=devicerole_switch,
            name="device2",
            location=location,
            status=status_active,
        )
        cls.bgp_routing_instance = models.BGPRoutingInstance.objects.create(
            description="Device 1 RI",
            autonomous_system=asn1,
            device=cls.device1,
            status=status_active,
        )

        cls.bgp_routing_instance_device_2 = models.BGPRoutingInstance.objects.create(
            description="Device 2 RI",
            autonomous_system=asn1,
            device=cls.device2,
            status=status_active,
        )

        interface_status = Status.objects.get_for_model(Interface).first()
        interfaces_device1 = [
            Interface.objects.create(device=cls.device1, name="Loopback0", status=interface_status),
            Interface.objects.create(device=cls.device1, name="Loopback1", status=interface_status),
            Interface.objects.create(device=cls.device1, name="Loopback2", status=interface_status),
        ]
        interfaces_device2 = [
            Interface.objects.create(device=cls.device2, name="Loopback0", status=interface_status),
            Interface.objects.create(device=cls.device2, name="Loopback1", status=interface_status),
        ]

        namespace = Namespace.objects.first()
        prefix_status = Status.objects.get_for_model(Prefix).first()
        Prefix.objects.create(prefix="10.0.0.0/8", namespace=namespace, status=prefix_status)

        addresses = [
            IPAddress.objects.create(
                address="10.1.1.1/24",
                status=status_active,
                namespace=namespace,
            ),
            IPAddress.objects.create(
                address="10.1.1.2/24",
                status=status_active,
                namespace=namespace,
            ),
            IPAddress.objects.create(
                address="10.1.1.3/24",
                status=status_active,
                namespace=namespace,
            ),
            IPAddress.objects.create(
                address="10.1.1.4/24",
                status=status_reserved,
                namespace=namespace,
            ),
            IPAddress.objects.create(
                address="10.1.1.5/24",
                status=status_active,
                namespace=namespace,
            ),
            IPAddress.objects.create(
                address="10.1.1.6/24",
                status=status_reserved,
                namespace=namespace,
            ),
            IPAddress.objects.create(
                address="10.1.1.7/24",
                status=status_reserved,
                namespace=namespace,
            ),
            IPAddress.objects.create(
                address="10.1.1.8/24",
                status=status_reserved,
                namespace=namespace,
            ),
            IPAddress.objects.create(
                address="10.1.1.9/24",
                status=status_reserved,
                namespace=namespace,
            ),
            IPAddress.objects.create(
                address="10.1.1.10/24",
                status=status_reserved,
                namespace=namespace,
            ),
        ]

        interfaces_device1[0].add_ip_addresses(addresses[0])
        interfaces_device1[1].add_ip_addresses(addresses[2])
        interfaces_device1[2].add_ip_addresses(addresses[4])

        interfaces_device2[0].add_ip_addresses(addresses[6])
        interfaces_device2[1].add_ip_addresses(addresses[8])

        # peeringrole_internal = models.PeeringRole.objects.create(name="Internal", slug="internal", color="ffffff")
        # peeringrole_external = models.PeeringRole.objects.create(name="External", slug="external", color="ffffff")
        peeringrole_internal = Role.objects.create(name="Internal", color="ffffff")
        peeringrole_internal.content_types.add(ContentType.objects.get_for_model(models.PeerEndpoint))
        peeringrole_external = Role.objects.create(name="External", color="ffffff")
        peeringrole_external.content_types.add(ContentType.objects.get_for_model(models.PeerEndpoint))

        peerings = [
            # Peering #0
            models.Peering.objects.create(status=status_active),
            # Peering #1
            models.Peering.objects.create(status=status_active),
            # Peering #2
            models.Peering.objects.create(status=status_reserved),
            # Peering #3
            models.Peering.objects.create(status=status_active),
            # Peering #4
            models.Peering.objects.create(status=status_active),
        ]

        # Peering #0
        models.PeerEndpoint.objects.create(
            source_ip=addresses[0],
            peering=peerings[0],
            autonomous_system=asn1,
            role=peeringrole_internal,
            routing_instance=cls.bgp_routing_instance,
        )
        models.PeerEndpoint.objects.create(
            source_ip=addresses[1],
            peering=peerings[0],
            autonomous_system=asn1,
            role=peeringrole_external,
        )

        # Peering #1
        models.PeerEndpoint.objects.create(
            source_ip=addresses[2],
            peering=peerings[1],
            autonomous_system=asn1,
            role=peeringrole_internal,
            routing_instance=cls.bgp_routing_instance,
        )
        models.PeerEndpoint.objects.create(
            source_ip=addresses[3],
            peering=peerings[1],
            autonomous_system=asn2,
            role=peeringrole_external,
        )

        # Peering #2
        models.PeerEndpoint.objects.create(
            source_ip=addresses[4],
            peering=peerings[2],
            autonomous_system=asn1,
            role=peeringrole_internal,
            routing_instance=cls.bgp_routing_instance,
        )
        models.PeerEndpoint.objects.create(
            source_ip=addresses[5],
            peering=peerings[2],
            autonomous_system=asn3,
            role=peeringrole_external,
        )

        # Peering #3
        models.PeerEndpoint.objects.create(
            source_ip=addresses[6],
            peering=peerings[3],
            autonomous_system=asn1,
            role=peeringrole_internal,
            routing_instance=cls.bgp_routing_instance_device_2,
        )
        models.PeerEndpoint.objects.create(
            source_ip=addresses[7],
            peering=peerings[3],
            autonomous_system=asn3,
            role=peeringrole_external,
        )

        # Peering #4
        models.PeerEndpoint.objects.create(
            source_ip=addresses[8],
            peering=peerings[4],
            autonomous_system=asn1,
            role=peeringrole_internal,
            routing_instance=cls.bgp_routing_instance_device_2,
        )
        models.PeerEndpoint.objects.create(
            source_ip=addresses[9],
            peering=peerings[4],
            autonomous_system=asn3,
            role=peeringrole_external,
        )

    def test_id(self):
        """Test filtering by id."""
        params = {"id": self.queryset.values_list("pk", flat=True)[:2]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    # def test_role(self):
    #     """Test filtering by role."""
    #     params = {"role": ["external"]}
    #     self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_status(self):
        """Test filtering by status."""
        params = {"status": [self.status_active.name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_device(self):
        """Test filtering by device name."""
        params = {"device": ["device1"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

        params = {"device": ["device2"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

        params = {"device": ["device1", "device2"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 5)

    def test_device_id(self):
        """Test filtering by device id."""
        params = {"device_id": [self.device1.id]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

        params = {"device_id": [self.device2.id]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

        params = {"device_id": [self.device1.pk, self.device2.id]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 5)

    def test_device_role(self):
        """Test filtering by device role name."""
        params = {"device_role": ["Router"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

        params = {"device_role": ["Switch"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

        params = {"device_role": ["Router", "Switch"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 5)

    def test_peer_endpoint_role(self):
        """Test filtering by peer endpoint role name."""
        params = {"peer_endpoint_role": ["internal"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 5)

        params = {"peer_endpoint_role": ["external"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 5)

        params = {"peer_endpoint_role": ["router", "switch"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 5)

    # def test_asn(self):
    #     """Test filtering by asn name."""
    #     params = {"asn": [65000]}
    #     self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
    #
    #     params = {"asn": [66000]}
    #     self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)
    #
    #     params = {"asn": [66000, 12345]}
    #     self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    # def test_address(self):
    #     """Test filtering by device name."""
    #     params = {"address": ["10.1.1.1"]}
    #     self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
    #
    #     params = {"address": ["10.1.1.1/32"]}
    #     self.assertEqual(self.filterset(params, self.queryset).qs.count(), 0)
    #
    #     params = {"address": ["10.1.1.1/24"]}
    #     self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
    #
    #     # Both IP addresses are part of the same Peering so only 1 Peering is expected
    #     params = {"address": ["10.1.1.1", "10.1.1.2"]}
    #     self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
    #
    #     params = {"address": ["10.1.1.3", "10.1.1.5"]}
    #     self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class AddressFamilyTestCase(TestCase):
    """Test filtering of AddressFamily records."""

    queryset = models.AddressFamily.objects.all()
    filterset = filters.AddressFamilyFilterSet

    @classmethod
    def setUpTestData(cls):  # pylint: disable=too-many-locals
        status_active = Status.objects.get(name__iexact="active")

        manufacturer = Manufacturer.objects.create(name="Cisco")
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model="CSR 1000V")
        location_type = LocationType.objects.create(name="site")
        location_status = Status.objects.get_for_model(Location).first()
        location = Location.objects.create(name="Site 1", location_type=location_type, status=location_status)
        devicerole = Role.objects.create(name="Router", color="ff0000")
        devicerole.content_types.add(ContentType.objects.get_for_model(Device))
        device1 = Device.objects.create(
            device_type=devicetype, role=devicerole, name="Device 1", location=location, status=status_active
        )
        interface_status = Status.objects.get_for_model(Interface).first()
        interface = Interface.objects.create(device=device1, name="Loopback1", status=interface_status)

        namespace = Namespace.objects.first()
        prefix_status = Status.objects.get_for_model(Prefix).first()
        Prefix.objects.create(prefix="1.0.0.0/8", namespace=namespace, status=prefix_status)

        address = IPAddress.objects.create(address="1.1.1.1/32", status=status_active, namespace=namespace)

        interface.add_ip_addresses(address)

        peeringrole = Role.objects.create(name="Internal", color="ffffff")
        peeringrole.content_types.add(ContentType.objects.get_for_model(models.PeerGroup))

        asn1 = models.AutonomousSystem.objects.create(asn=65000, status=status_active)

        cls.bgp_routing_instance = models.BGPRoutingInstance.objects.create(
            description="Hello World!",
            autonomous_system=asn1,
            device=device1,
            status=status_active,
        )

        cls.peergroup = models.PeerGroup.objects.create(
            routing_instance=cls.bgp_routing_instance,
            name="Group B",
            role=peeringrole,
        )

        peering = models.Peering.objects.create(status=status_active)
        cls.endpoint = models.PeerEndpoint.objects.create(
            routing_instance=cls.bgp_routing_instance,
            source_ip=address,
            peering=peering,
        )

        models.AddressFamily.objects.create(
            routing_instance=cls.bgp_routing_instance,
            afi_safi=choices.AFISAFIChoices.AFI_IPV4_UNICAST,
        )

        models.AddressFamily.objects.create(
            routing_instance=cls.bgp_routing_instance,
            afi_safi=choices.AFISAFIChoices.AFI_IPV4_FLOWSPEC,
        )

        models.AddressFamily.objects.create(
            routing_instance=cls.bgp_routing_instance,
            afi_safi=choices.AFISAFIChoices.AFI_VPNV4_UNICAST,
        )

    def test_id(self):
        """Test filtering by id."""
        params = {"id": self.queryset.values_list("pk", flat=True)[:2]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_afi_safi(self):
        """Test filtering by AFI-SAFI."""
        params = {"afi_safi": ["ipv4_unicast", "vpnv4_unicast"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    # TODO filtering by device/virtualmachine
    def test_device(self):
        pass


class PeerGroupAddressFamilyTestCase(TestCase):
    """Test filtering of PeerGroupAddressFamily records."""

    queryset = models.PeerGroupAddressFamily.objects.all()
    filterset = filters.PeerGroupAddressFamilyFilterSet

    @classmethod
    def setUpTestData(cls):
        """One-time class setup."""
        status_active = Status.objects.get(name__iexact="active")
        status_active.content_types.add(ContentType.objects.get_for_model(models.AutonomousSystem))

        manufacturer = Manufacturer.objects.create(name="Cisco")
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model="CSR 1000V")

        location_type = LocationType.objects.create(name="site")
        location_status = Status.objects.get_for_model(Location).first()
        location = Location.objects.create(name="Site 1", location_type=location_type, status=location_status)
        devicerole = Role.objects.create(name="Router", color="ff0000")

        cls.device_1 = Device.objects.create(
            device_type=devicetype, role=devicerole, name="Device 1", location=location, status=status_active
        )

        cls.asn_1 = models.AutonomousSystem.objects.create(asn=4294967294, status=status_active)

        cls.peeringrole_internal = Role.objects.create(name="Internal", color="ffffff")
        cls.peeringrole_internal.content_types.add(ContentType.objects.get_for_model(models.PeerGroup))

        peeringrole_external = Role.objects.create(name="External", color="ffffff")
        peeringrole_external.content_types.add(ContentType.objects.get_for_model(models.PeerGroup))

        cls.bgp_routing_instance = models.BGPRoutingInstance.objects.create(
            description="Hello World!",
            autonomous_system=cls.asn_1,
            device=cls.device_1,
            status=status_active,
        )

        cls.pg1 = models.PeerGroup.objects.create(
            routing_instance=cls.bgp_routing_instance,
            name="Group A",
            role=cls.peeringrole_internal,
            autonomous_system=cls.asn_1,
            description="Internal Group",
        )
        cls.pg2 = models.PeerGroup.objects.create(
            routing_instance=cls.bgp_routing_instance,
            name="Group B",
            role=peeringrole_external,
            autonomous_system=cls.asn_1,
            enabled=False,
            description="External Group",
        )

        models.PeerGroupAddressFamily.objects.create(
            peer_group=cls.pg1,
            afi_safi="ipv4_unicast",
        )
        models.PeerGroupAddressFamily.objects.create(
            peer_group=cls.pg1,
            afi_safi="ipv6_unicast",
        )
        models.PeerGroupAddressFamily.objects.create(
            peer_group=cls.pg2,
            afi_safi="ipv4_unicast",
        )

    def test_search(self):
        """Test text search."""
        self.assertEqual(self.filterset({"q": "ipv4"}, self.queryset).qs.count(), 2)
        self.assertEqual(self.filterset({"q": self.pg1.name}, self.queryset).qs.count(), 2)
        self.assertEqual(self.filterset({"q": self.pg1.description}, self.queryset).qs.count(), 2)

    def test_id(self):
        """Test filtering by ID (primary key)."""
        self.assertEqual(
            self.filterset({"id": self.queryset.values_list("pk", flat=True)[:2]}, self.queryset).qs.count(),
            2,
        )

    def test_afi_safi(self):
        """Test filtering by afi_safi."""
        self.assertEqual(self.filterset({"afi_safi": ["ipv4_unicast"]}, self.queryset).qs.count(), 2)

    def test_peer_endpoint(self):
        """Test filtering by peer_group."""
        self.assertEqual(self.filterset({"peer_group": [self.pg1.pk]}, self.queryset).qs.count(), 2)


class PeerEndpointAddressFamilyTestCase(TestCase):
    """Test filtering of PeerEndpointAddressFamily records."""

    queryset = models.PeerEndpointAddressFamily.objects.all()
    filterset = filters.PeerEndpointAddressFamilyFilterSet

    @classmethod
    def setUpTestData(cls):
        """One-time class setup."""
        status_active = Status.objects.get(name__iexact="active")
        status_active.content_types.add(ContentType.objects.get_for_model(models.AutonomousSystem))
        status_active.content_types.add(ContentType.objects.get_for_model(Interface))

        cls.namespace = Namespace.objects.first()
        prefix_status = Status.objects.get_for_model(Prefix).first()
        Prefix.objects.create(prefix="1.0.0.0/8", namespace=cls.namespace, status=prefix_status)

        # provider = Provider.objects.create(name="Provider", slug="provider")

        asn = models.AutonomousSystem.objects.create(asn=4294967295, status=status_active)
        # asn_15521 = models.AutonomousSystem.objects.create(asn=15521, status=status_active, provider=provider)

        peeringrole = Role.objects.create(name="Internal", color="ffffff")
        peeringrole.content_types.add(ContentType.objects.get_for_model(models.PeerEndpoint))

        manufacturer = Manufacturer.objects.create(name="Cisco")
        cls.devicetype = DeviceType.objects.create(manufacturer=manufacturer, model="CSR 1000V")

        location_type = LocationType.objects.create(name="site")
        location_status = Status.objects.get_for_model(Location).first()
        cls.location = Location.objects.create(name="Site 1", location_type=location_type, status=location_status)
        cls.devicerole = Role.objects.create(name="Router", color="ff0000")
        cls.devicerole.content_types.add(ContentType.objects.get_for_model(Device))

        device = Device.objects.create(
            device_type=cls.devicetype,
            role=cls.devicerole,
            name="Device 1",
            location=cls.location,
            status=status_active,
        )
        interface = Interface.objects.create(
            device=device,
            name="Loopback1",
            type=InterfaceTypeChoices.TYPE_VIRTUAL,
            status=status_active,
        )

        addresses = [
            IPAddress.objects.create(address="1.1.1.1/32", status=status_active, namespace=cls.namespace),
            IPAddress.objects.create(address="1.1.1.2/32", status=status_active, namespace=cls.namespace),
            IPAddress.objects.create(address="1.1.1.3/32", status=status_active, namespace=cls.namespace),
        ]

        interface.add_ip_addresses(
            [
                addresses[0],
                addresses[1],
            ]
        )

        cls.bgp_routing_instance = models.BGPRoutingInstance.objects.create(
            description="Hello World!",
            autonomous_system=asn,
            device=device,
            status=status_active,
        )

        cls.peergroup = models.PeerGroup.objects.create(
            name="Group B",
            role=peeringrole,
            routing_instance=cls.bgp_routing_instance,
        )

        peering1 = models.Peering.objects.create(status=status_active)
        peering2 = models.Peering.objects.create(status=status_active)
        peering3 = models.Peering.objects.create(status=status_active)

        cls.pe1 = models.PeerEndpoint.objects.create(
            routing_instance=cls.bgp_routing_instance,
            source_ip=addresses[0],
            autonomous_system=asn,
            peering=peering1,
            description="I'm an endpoint!",
        )
        cls.pe2 = models.PeerEndpoint.objects.create(
            routing_instance=cls.bgp_routing_instance,
            source_ip=addresses[1],
            autonomous_system=asn,
            peer_group=cls.peergroup,
            peering=peering2,
        )
        cls.pe3 = models.PeerEndpoint.objects.create(
            source_ip=addresses[2],
            peer_group=cls.peergroup,
            enabled=False,
            peering=peering3,
        )

        models.PeerEndpointAddressFamily.objects.create(
            peer_endpoint=cls.pe1,
            afi_safi="ipv4_unicast",
        )
        models.PeerEndpointAddressFamily.objects.create(
            peer_endpoint=cls.pe1,
            afi_safi="ipv6_unicast",
        )
        models.PeerEndpointAddressFamily.objects.create(
            peer_endpoint=cls.pe2,
            afi_safi="ipv4_unicast",
        )
        models.PeerEndpointAddressFamily.objects.create(
            peer_endpoint=cls.pe3,
            afi_safi="ipv4_unicast",
        )

    def test_search(self):
        """Test text search."""
        self.assertEqual(self.filterset({"q": "ipv4_unicast"}, self.queryset).qs.count(), 3)
        self.assertEqual(self.filterset({"q": self.pe1.description}, self.queryset).qs.count(), 2)

    def test_id(self):
        """Test filtering by ID (primary key)."""
        self.assertEqual(
            self.filterset({"id": self.queryset.values_list("pk", flat=True)[:2]}, self.queryset).qs.count(),
            2,
        )

    def test_afi_safi(self):
        """Test filtering by AFI-SAFI."""
        self.assertEqual(self.filterset({"afi_safi": ["ipv4_unicast"]}, self.queryset).qs.count(), 3)

    def test_peer_endpoint(self):
        """Test filtering by peer_endpoint."""
        self.assertEqual(self.filterset({"peer_endpoint": [self.pe1.pk, self.pe2.pk]}, self.queryset).qs.count(), 3)
