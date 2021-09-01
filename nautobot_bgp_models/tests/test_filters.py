"""Unit test automation for FilterSet classes in nautobot_bgp_models."""

from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from nautobot.dcim.models import Device, DeviceRole, DeviceType, Interface, Manufacturer, Site
from nautobot.extras.models import Status, Relationship, RelationshipAssociation
from nautobot.ipam.models import IPAddress, VRF

from nautobot_bgp_models import choices, filters, models


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
        device_2 = Device.objects.create(
            device_type=devicetype, device_role=devicerole, name="Device 2", site=site, status=status_active
        )

        cls.vrf = VRF.objects.create(name="Ark B")

        cls.asn_1 = models.AutonomousSystem.objects.create(asn=4294967294, status=status_active)
        asn_2 = models.AutonomousSystem.objects.create(asn=4294967295, status=status_active)

        cls.peeringrole_internal = models.PeeringRole.objects.create(name="Internal", slug="internal", color="333333")
        peeringrole_external = models.PeeringRole.objects.create(name="External", slug="external", color="ffffff")

        models.PeerGroup.objects.create(
            name="Group A", device=cls.device_1, role=cls.peeringrole_internal, autonomous_system=cls.asn_1
        )
        models.PeerGroup.objects.create(
            name="Group B", device=cls.device_1, role=peeringrole_external, autonomous_system=cls.asn_1, enabled=False
        )
        models.PeerGroup.objects.create(
            name="Group A", device=device_2, role=cls.peeringrole_internal, autonomous_system=asn_2, vrf=cls.vrf
        )

    def test_search(self):
        """Test text search."""
        # Match on name (case-insensitive)
        self.assertEqual(self.filterset({"q": "Group A"}, self.queryset).qs.count(), 2)
        self.assertEqual(self.filterset({"q": "group a"}, self.queryset).qs.count(), 2)
        # TODO: match on Device / VirtualMachine name too?

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

    def test_vrf(self):
        """Test filtering by VRF."""
        params = {"vrf": [self.vrf.name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)


class PeerEndpointTestCase(TestCase):
    """Test filtering of PeerEndpoint records."""

    queryset = models.PeerEndpoint.objects.all()
    filterset = filters.PeerEndpointFilterSet

    @classmethod
    def setUpTestData(cls):
        """One-time class setup."""
        status_active = Status.objects.get(slug="active")
        status_active.content_types.add(ContentType.objects.get_for_model(models.AutonomousSystem))

        vrf = VRF.objects.create(name="Ark B")
        addresses = [
            IPAddress.objects.create(address="1.1.1.1/32", status=status_active),
            IPAddress.objects.create(address="1.1.1.1/32", status=status_active, vrf=vrf),
            IPAddress.objects.create(address="1.1.1.2/32", status=status_active, vrf=vrf),
        ]

        manufacturer = Manufacturer.objects.create(name="Cisco", slug="cisco")
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model="CSR 1000V", slug="csr1000v")
        site = Site.objects.create(name="Site 1", slug="site-1")
        devicerole = DeviceRole.objects.create(name="Router", slug="router", color="ff0000")
        device = Device.objects.create(
            device_type=devicetype, device_role=devicerole, name="Device 1", site=site, status=status_active
        )

        asn = models.AutonomousSystem.objects.create(asn=4294967295, status=status_active)
        peeringrole = models.PeeringRole.objects.create(name="Internal", slug="internal", color="ffffff")
        cls.peergroup = models.PeerGroup.objects.create(device=device, name="Group B", role=peeringrole)

        peersession1 = models.PeerSession.objects.create(role=peeringrole, status=status_active)
        peersession2 = models.PeerSession.objects.create(role=peeringrole, status=status_active)
        peersession3 = models.PeerSession.objects.create(role=peeringrole, status=status_active)
        models.PeerEndpoint.objects.create(local_ip=addresses[0], autonomous_system=asn, session=peersession1)
        models.PeerEndpoint.objects.create(
            local_ip=addresses[1],
            autonomous_system=asn,
            vrf=vrf,
            peer_group=cls.peergroup,
            session=peersession2,
        )
        models.PeerEndpoint.objects.create(
            local_ip=addresses[2],
            vrf=vrf,
            peer_group=cls.peergroup,
            enabled=False,
            session=peersession3,
        )

    def test_search(self):
        """Test text search."""
        # TODO match on device/virtual machine name
        # Match on peer-group name (case-insensitive)
        self.assertEqual(self.filterset({"q": "Group B"}, self.queryset).qs.count(), 2)
        self.assertEqual(self.filterset({"q": "group b"}, self.queryset).qs.count(), 2)

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

    def test_vrf(self):
        """Test filtering by VRF."""
        params = {"vrf": ["Ark B"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_peer_group(self):
        """Test filtering by peer-group."""
        params = {"peer_group": [self.peergroup.pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class PeerSessionTestCase(TestCase):
    """Test filtering of PeerSession records."""

    queryset = models.PeerSession.objects.all()
    filterset = filters.PeerSessionFilterSet

    @classmethod
    def setUpTestData(cls):  # pylint: disable=too-many-locals
        """One-time class setup to prepopulate required data for tests."""
        status_active = Status.objects.get(slug="active")
        status_active.content_types.add(ContentType.objects.get_for_model(models.PeerSession))
        status_active.content_types.add(ContentType.objects.get_for_model(models.AutonomousSystem))

        status_reserved = Status.objects.get(slug="reserved")
        status_reserved.content_types.add(ContentType.objects.get_for_model(models.PeerSession))

        asn1 = models.AutonomousSystem.objects.create(asn=65000, status=status_active)
        asn2 = models.AutonomousSystem.objects.create(asn=66000, status=status_active)
        asn3 = models.AutonomousSystem.objects.create(asn=12345, status=status_active)

        manufacturer = Manufacturer.objects.create(name="Cisco", slug="cisco")
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model="CSR 1000V", slug="csr1000v")
        site = Site.objects.create(name="Site 1", slug="site-1")
        devicerole = DeviceRole.objects.create(name="Router", slug="router", color="ff0000")
        device1 = Device.objects.create(
            device_type=devicetype, device_role=devicerole, name="device1", site=site, status=status_active
        )
        device2 = Device.objects.create(
            device_type=devicetype, device_role=devicerole, name="device2", site=site, status=status_active
        )
        interfaces_device1 = [
            Interface.objects.create(device=device1, name="Loopback0"),
            Interface.objects.create(device=device1, name="Loopback1"),
            Interface.objects.create(device=device1, name="Loopback2"),
        ]
        interfaces_device2 = [
            Interface.objects.create(device=device2, name="Loopback0"),
            Interface.objects.create(device=device2, name="Loopback1"),
            Interface.objects.create(device=device2, name="Loopback2"),
        ]

        rel = Relationship.objects.get(slug="bgp_asn")
        RelationshipAssociation.objects.create(relationship=rel, source=asn2, destination=device2)

        addresses = [
            IPAddress.objects.create(
                address="10.1.1.1/24", status=status_active, assigned_object=interfaces_device1[0]
            ),
            IPAddress.objects.create(
                address="10.1.1.2/24", status=status_active, assigned_object=interfaces_device2[0]
            ),
            IPAddress.objects.create(
                address="10.1.1.3/24", status=status_active, assigned_object=interfaces_device1[1]
            ),
            IPAddress.objects.create(address="10.1.1.4/24", status=status_reserved),
            IPAddress.objects.create(address="10.1.1.5/24", status=status_active),
            IPAddress.objects.create(
                address="10.1.1.6/24", status=status_reserved, assigned_object=interfaces_device2[0]
            ),
        ]

        endpoints = [
            models.PeerEndpoint.objects.create(local_ip=addresses[0], autonomous_system=asn1),
            models.PeerEndpoint.objects.create(local_ip=addresses[1]),
            models.PeerEndpoint.objects.create(local_ip=addresses[2], autonomous_system=asn2),
            models.PeerEndpoint.objects.create(local_ip=addresses[3]),
            models.PeerEndpoint.objects.create(local_ip=addresses[4]),
            models.PeerEndpoint.objects.create(local_ip=addresses[5], autonomous_system=asn3),
        ]

        peeringrole_internal = models.PeeringRole.objects.create(name="Internal", slug="internal", color="ffffff")
        peeringrole_external = models.PeeringRole.objects.create(name="External", slug="external", color="ffffff")

        sessions = [
            models.PeerSession.objects.create(status=status_active, role=peeringrole_internal),
            models.PeerSession.objects.create(status=status_active, role=peeringrole_external),
            models.PeerSession.objects.create(status=status_reserved, role=peeringrole_external),
        ]

        models.PeerEndpoint.objects.create(local_ip=addresses[0], session=sessions[0])
        models.PeerEndpoint.objects.create(local_ip=addresses[1], session=sessions[0])
        models.PeerEndpoint.objects.create(local_ip=addresses[2], session=sessions[1])
        models.PeerEndpoint.objects.create(local_ip=addresses[3], session=sessions[1])
        models.PeerEndpoint.objects.create(local_ip=addresses[4], session=sessions[2])
        models.PeerEndpoint.objects.create(local_ip=addresses[5], session=sessions[2])

    def test_id(self):
        """Test filtering by id."""
        params = {"id": self.queryset.values_list("pk", flat=True)[:2]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_role(self):
        """Test filtering by role."""
        params = {"role": ["external"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_status(self):
        """Test filtering by status."""
        params = {"status": ["active"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_device(self):
        """Test filtering by device name."""
        params = {"device": ["device1"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

        params = {"device": ["device1", "device2"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_asn(self):
        """Test filtering by asn name."""
        params = {"asn": [65000]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

        params = {"asn": [66000]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

        params = {"asn": [66000, 12345]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_address(self):
        """Test filtering by device name."""
        params = {"address": ["10.1.1.1"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

        params = {"address": ["10.1.1.1/32"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 0)

        params = {"address": ["10.1.1.1/24"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

        params = {"address": ["10.1.1.1", "10.1.1.2"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

        params = {"address": ["10.1.1.3", "10.1.1.5"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


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
        device = Device.objects.create(
            device_type=devicetype, device_role=devicerole, name="Device 1", site=site, status=status_active
        )
        interface = Interface.objects.create(device=device, name="Loopback1")
        address = IPAddress.objects.create(address="1.1.1.1/32", status=status_active, assigned_object=interface)

        peeringrole = models.PeeringRole.objects.create(name="Internal", slug="internal", color="ffffff")
        cls.peergroup = models.PeerGroup.objects.create(device=device, name="Group B", role=peeringrole)

        peersession = models.PeerSession.objects.create(status=status_active, role=peeringrole)
        cls.endpoint = models.PeerEndpoint.objects.create(local_ip=address, session=peersession)

        models.AddressFamily.objects.create(
            afi_safi=choices.AFISAFIChoices.AFI_IPV4,
            device=device,
        )
        models.AddressFamily.objects.create(
            afi_safi=choices.AFISAFIChoices.AFI_IPV4_FLOWSPEC,
            device=device,
            peer_group=cls.peergroup,
        )
        models.AddressFamily.objects.create(
            afi_safi=choices.AFISAFIChoices.AFI_VPNV4,
            device=device,
            peer_endpoint=cls.endpoint,
        )

    def test_id(self):
        """Test filtering by id."""
        params = {"id": self.queryset.values_list("pk", flat=True)[:2]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_afi_safi(self):
        """Test filtering by AFI-SAFI."""
        params = {"afi_safi": ["ipv4", "vpnv4"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    # TODO filtering by device/virtualmachine

    def test_peer_group(self):
        """Test filtering by peer-group."""
        params = {"peer_group": [self.peergroup.pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_peer_endpoint(self):
        """Test filtering by peer endpoint."""
        params = {"peer_endpoint": [self.endpoint.pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
