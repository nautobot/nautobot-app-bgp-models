"""Unit test automation for FilterSet classes in nautobot_bgp_models."""

from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

# from nautobot.circuits.models import Provider
from nautobot.dcim.choices import InterfaceTypeChoices
from nautobot.dcim.models import Device, DeviceRole, DeviceType, Interface, Manufacturer, Site
from nautobot.extras.models import Status
from nautobot.ipam.models import IPAddress


from nautobot_bgp_models import filters, models, choices


class AutonomousSystemTestCase(TestCase):
    """Test filtering of AutonomousSystem records."""

    queryset = models.AutonomousSystem.objects.all()
    filterset = filters.AutonomousSystemFilterSet

    @classmethod
    def setUpTestData(cls):
        """One-time class setup to prepopulate required data for tests."""
        status_active = Status.objects.get(slug="active")
        status_active.content_types.add(ContentType.objects.get_for_model(models.AutonomousSystem))

        status_primary_asn = Status.objects.create(name="Primary ASN", slug="primary-asn", color="FFFFFF")
        status_primary_asn.content_types.add(ContentType.objects.get_for_model(models.AutonomousSystem))

        status_remote_asn = Status.objects.create(name="Remote ASN", slug="remote-asn", color="FFFFFF")
        status_remote_asn.content_types.add(ContentType.objects.get_for_model(models.AutonomousSystem))

        models.AutonomousSystem.objects.create(
            asn=4200000000, status=status_active, description="Reserved for private use"
        )
        models.AutonomousSystem.objects.create(
            asn=4200000001, status=status_primary_asn, description="Also reserved for private use"
        )
        models.AutonomousSystem.objects.create(
            asn=4200000002, status=status_remote_asn, description="Another reserved for private use"
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
        params = {"status": ["primary-asn", "remote-asn"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class PeeringRoleTestCase(TestCase):
    """Test filtering of PeeringRole records."""

    queryset = models.PeeringRole.objects.all()
    filterset = filters.PeeringRoleFilterSet

    @classmethod
    def setUpTestData(cls):
        """One-time class setup to prepopulate required data for tests."""
        models.PeeringRole.objects.create(name="Alpha", slug="alpha", color="ff0000", description="Actually omega")
        models.PeeringRole.objects.create(name="Beta", slug="beta", color="00ff00")
        models.PeeringRole.objects.create(name="Gamma", slug="gamma", color="0000ff")

    def test_search(self):
        """Test text search."""
        # Match on name/slug (case-insensitive)
        self.assertEqual(self.filterset({"q": "Alpha"}, self.queryset).qs.count(), 1)
        self.assertEqual(self.filterset({"q": "ALPHA"}, self.queryset).qs.count(), 1)
        # Match on description
        self.assertEqual(self.filterset({"q": "actually"}, self.queryset).qs.count(), 1)

    def test_id(self):
        """Test filtering by ID (primary key)."""
        params = {"id": self.queryset.values_list("pk", flat=True)[:2]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_name(self):
        """Test filtering by name field."""
        params = {"name": ["Alpha", "Beta"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_slug(self):
        """Test filtering by slug field."""
        params = {"slug": ["alpha", "gamma"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_color(self):
        """Test filtering by color field."""
        params = {"color": ["ff0000", "0000ff"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class PeerGroupTestCase(TestCase):
    """Test filtering of PeerGroup records."""

    queryset = models.PeerGroup.objects.all()
    filterset = filters.PeerGroupFilterSet

    @classmethod
    def setUpTestData(cls):
        """One-time class setup."""
        status_active = Status.objects.get(slug="active")
        status_active.content_types.add(ContentType.objects.get_for_model(models.AutonomousSystem))

        manufacturer = Manufacturer.objects.create(name="Cisco", slug="cisco")
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model="CSR 1000V", slug="csr1000v")
        site = Site.objects.create(name="Site 1", slug="site-1")
        devicerole = DeviceRole.objects.create(name="Router", slug="router", color="ff0000")
        cls.device_1 = Device.objects.create(
            device_type=devicetype, device_role=devicerole, name="Device 1", site=site, status=status_active
        )

        cls.asn_1 = models.AutonomousSystem.objects.create(asn=4294967294, status=status_active)
        asn_2 = models.AutonomousSystem.objects.create(asn=4294967295, status=status_active)

        cls.peeringrole_internal = models.PeeringRole.objects.create(name="Internal", slug="internal", color="333333")
        peeringrole_external = models.PeeringRole.objects.create(name="External", slug="external", color="ffffff")

        cls.bgp_routing_instance = models.BGPRoutingInstance.objects.create(
            description="Hello World!",
            autonomous_system=cls.asn_1,
            device=cls.device_1,
            status=status_active,
        )

        models.PeerGroup.objects.create(
            routing_instance=cls.bgp_routing_instance,
            name="Group A",
            role=cls.peeringrole_internal,
            autonomous_system=cls.asn_1,
            description="Internal Group",
        )
        models.PeerGroup.objects.create(
            routing_instance=cls.bgp_routing_instance,
            name="Group B",
            role=peeringrole_external,
            autonomous_system=cls.asn_1,
            enabled=False,
            description="External Group",
        )
        models.PeerGroup.objects.create(
            routing_instance=cls.bgp_routing_instance,
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
        self.assertEqual(self.filterset({"q": "Internal Group"}, self.queryset).qs.count(), 2)
        self.assertEqual(self.filterset({"q": "External Group"}, self.queryset).qs.count(), 1)

    def test_id(self):
        """Test filtering by ID (primary key)."""
        params = {"id": self.queryset.values_list("pk", flat=True)[:2]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_enabled(self):
        """Test filtering by enabled status."""
        params = {"enabled": True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_role(self):
        """Test filtering by peering role."""
        params = {"role": [self.peeringrole_internal.slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_autonomous_system(self):
        """Test filtering by autonomous system."""
        params = {"autonomous_system": [4294967294]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_routing_instance(self):
        """Test Routing Instance."""
        self.assertEqual(
            self.filterset({"routing_instance": self.bgp_routing_instance.pk}, self.queryset).qs.count(), 3
        )


class PeerEndpointTestCase(TestCase):
    """Test filtering of PeerEndpoint records."""

    queryset = models.PeerEndpoint.objects.all()
    filterset = filters.PeerEndpointFilterSet

    @classmethod
    def setUpTestData(cls):
        """One-time class setup."""
        status_active = Status.objects.get(slug="active")
        status_active.content_types.add(ContentType.objects.get_for_model(models.AutonomousSystem))

        # provider = Provider.objects.create(name="Provider", slug="provider")

        asn = models.AutonomousSystem.objects.create(asn=4294967295, status=status_active)
        # asn_15521 = models.AutonomousSystem.objects.create(asn=15521, status=status_active, provider=provider)

        peeringrole = models.PeeringRole.objects.create(name="Internal", slug="internal", color="ffffff")
        manufacturer = Manufacturer.objects.create(name="Cisco", slug="cisco")
        cls.devicetype = DeviceType.objects.create(manufacturer=manufacturer, model="CSR 1000V", slug="csr1000v")
        cls.site = Site.objects.create(name="Site 1", slug="site-1")
        cls.devicerole = DeviceRole.objects.create(name="Router", slug="router", color="ff0000")
        device = Device.objects.create(
            device_type=cls.devicetype,
            device_role=cls.devicerole,
            name="Device 1",
            site=cls.site,
            status=status_active,
        )
        interface = Interface.objects.create(device=device, name="Loopback1", type=InterfaceTypeChoices.TYPE_VIRTUAL)

        addresses = [
            IPAddress.objects.create(address="1.1.1.1/32", status=status_active, assigned_object=interface),
            IPAddress.objects.create(address="1.1.1.2/32", status=status_active, assigned_object=interface),
            IPAddress.objects.create(address="1.1.1.3/32", status=status_active),
        ]

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


class PeeringTestCase(TestCase):
    """Test filtering of Peering records."""

    queryset = models.Peering.objects.all()
    filterset = filters.PeeringFilterSet

    @classmethod
    def setUpTestData(cls):  # pylint: disable=too-many-locals
        """One-time class setup to prepopulate required data for tests."""
        status_active = Status.objects.get(slug="active")
        status_active.content_types.add(ContentType.objects.get_for_model(models.Peering))
        status_active.content_types.add(ContentType.objects.get_for_model(models.AutonomousSystem))

        status_reserved = Status.objects.get(slug="reserved")
        status_reserved.content_types.add(ContentType.objects.get_for_model(models.Peering))

        asn1 = models.AutonomousSystem.objects.create(asn=65000, status=status_active)
        asn2 = models.AutonomousSystem.objects.create(asn=66000, status=status_active)
        asn3 = models.AutonomousSystem.objects.create(asn=12345, status=status_active)

        manufacturer = Manufacturer.objects.create(name="Cisco", slug="cisco")
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model="CSR 1000V", slug="csr1000v")
        site = Site.objects.create(name="Site 1", slug="site-1")
        devicerole_router = DeviceRole.objects.create(name="Router", slug="router", color="ff0000")
        devicerole_switch = DeviceRole.objects.create(name="Switch", slug="switch", color="ff0000")
        device1 = Device.objects.create(
            device_type=devicetype,
            device_role=devicerole_router,
            name="device1",
            site=site,
            status=status_active,
        )
        device2 = Device.objects.create(
            device_type=devicetype,
            device_role=devicerole_switch,
            name="device2",
            site=site,
            status=status_active,
        )
        cls.bgp_routing_instance = models.BGPRoutingInstance.objects.create(
            description="Device 1 RI",
            autonomous_system=asn1,
            device=device1,
            status=status_active,
        )

        cls.bgp_routing_instance_device_2 = models.BGPRoutingInstance.objects.create(
            description="Device 2 RI",
            autonomous_system=asn1,
            device=device2,
            status=status_active,
        )

        interfaces_device1 = [
            Interface.objects.create(device=device1, name="Loopback0"),
            Interface.objects.create(device=device1, name="Loopback1"),
            Interface.objects.create(device=device1, name="Loopback2"),
        ]
        interfaces_device2 = [
            Interface.objects.create(device=device2, name="Loopback0"),
            Interface.objects.create(device=device2, name="Loopback1"),
        ]

        addresses = [
            IPAddress.objects.create(
                address="10.1.1.1/24",
                status=status_active,
                assigned_object=interfaces_device1[0],
            ),
            IPAddress.objects.create(
                address="10.1.1.2/24",
                status=status_active,
            ),
            IPAddress.objects.create(
                address="10.1.1.3/24",
                status=status_active,
                assigned_object=interfaces_device1[1],
            ),
            IPAddress.objects.create(
                address="10.1.1.4/24",
                status=status_reserved,
            ),
            IPAddress.objects.create(
                address="10.1.1.5/24",
                status=status_active,
                assigned_object=interfaces_device1[2],
            ),
            IPAddress.objects.create(
                address="10.1.1.6/24",
                status=status_reserved,
            ),
            IPAddress.objects.create(
                address="10.1.1.7/24",
                status=status_reserved,
                assigned_object=interfaces_device2[0],
            ),
            IPAddress.objects.create(
                address="10.1.1.8/24",
                status=status_reserved,
            ),
            IPAddress.objects.create(
                address="10.1.1.9/24",
                status=status_reserved,
                assigned_object=interfaces_device2[1],
            ),
            IPAddress.objects.create(
                address="10.1.1.10/24",
                status=status_reserved,
            ),
        ]

        peeringrole_internal = models.PeeringRole.objects.create(name="Internal", slug="internal", color="ffffff")
        peeringrole_external = models.PeeringRole.objects.create(name="External", slug="external", color="ffffff")

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

    def test_status(self):
        """Test filtering by status."""
        params = {"status": ["active"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_device(self):
        """Test filtering by device name."""
        params = {"device": ["device1"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

        params = {"device": ["device2"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

        params = {"device": ["device1", "device2"]}
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
    def setUpTestData(cls):
        status_active = Status.objects.get(slug="active")

        manufacturer = Manufacturer.objects.create(name="Cisco", slug="cisco")
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model="CSR 1000V", slug="csr1000v")
        site = Site.objects.create(name="Site 1", slug="site-1")
        devicerole = DeviceRole.objects.create(name="Router", slug="router", color="ff0000")
        device1 = Device.objects.create(
            device_type=devicetype, device_role=devicerole, name="Device 1", site=site, status=status_active
        )
        interface = Interface.objects.create(device=device1, name="Loopback1")
        address = IPAddress.objects.create(address="1.1.1.1/32", status=status_active, assigned_object=interface)

        peeringrole = models.PeeringRole.objects.create(name="Internal", slug="internal", color="ffffff")

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
