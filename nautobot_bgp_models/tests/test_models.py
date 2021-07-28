"""Unit test automation for Model classes in nautobot_bgp_models."""

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.test import TestCase

from nautobot.dcim.models import Device, DeviceRole, DeviceType, Interface, Manufacturer, Site
from nautobot.extras.models import Status
from nautobot.ipam.models import IPAddress, VRF

from nautobot_bgp_models import models
from nautobot_bgp_models.choices import AFISAFIChoices


class AutonomousSystemTestCase(TestCase):
    """Test the AutonomousSystem model."""

    @classmethod
    def setUpTestData(cls):
        """One-time class data setup."""
        status_active = Status.objects.get(slug="active")
        status_active.content_types.add(ContentType.objects.get_for_model(models.AutonomousSystem))

        cls.autonomous_system = models.AutonomousSystem.objects.create(
            asn=12345, status=status_active, description="Hello!"
        )

    def test_str(self):
        """Test string representation of an AutonomousSystem."""
        self.assertEqual(str(self.autonomous_system), "AS 12345")

    def test_to_csv(self):
        """Test CSV representation of an AutonomousSystem."""
        self.assertEqual(self.autonomous_system.to_csv(), (12345, "Hello!", "Active"))


class PeeringRoleTestCase(TestCase):
    """Test the PeeringRole model."""

    @classmethod
    def setUpTestData(cls):
        """One-time class data setup."""
        cls.peering_role = models.PeeringRole.objects.create(
            name="Internal", slug="internal", color="00ff00", description="Hello!"
        )

    def test_str(self):
        """Test string representation of a PeeringRole."""
        self.assertEqual(str(self.peering_role), self.peering_role.name)

    def test_to_csv(self):
        """Test CSV representation of a PeeringRole."""
        self.assertEqual(self.peering_role.to_csv(), ("Internal", "internal", "00ff00", "Hello!"))


class PeerGroupTestCase(TestCase):
    """Test the PeerGroup model."""

    @classmethod
    def setUpTestData(cls):
        """One-time class data setup."""
        cls.status_active = Status.objects.get(slug="active")

        manufacturer = Manufacturer.objects.create(name="Cisco", slug="cisco")
        cls.devicetype = DeviceType.objects.create(manufacturer=manufacturer, model="CSR 1000V", slug="csr1000v")
        cls.site = Site.objects.create(name="Site 1", slug="site-1")
        cls.devicerole = DeviceRole.objects.create(name="Router", slug="router", color="ff0000")

        cls.peeringrole_internal = models.PeeringRole.objects.create(name="Internal", slug="internal", color="333333")

    def setUp(self):
        """Per-test data setup."""
        self.device_1 = Device.objects.create(
            device_type=self.devicetype,
            device_role=self.devicerole,
            name="Device 1",
            site=self.site,
            status=self.status_active,
        )
        self.peergroup = models.PeerGroup.objects.create(
            name="Peer Group A", device=self.device_1, role=self.peeringrole_internal
        )

    def test_str(self):
        """Test string representation of a PeerGroup."""
        self.assertEqual(str(self.peergroup), f"{self.peergroup.name} on {self.device_1.name}")

    def test_vrf_fixup_from_router_id(self):
        """If VRF is None, but the router-id references a VRF, use that."""
        vrf = VRF.objects.create(name="red")
        self.peergroup.router_id = IPAddress.objects.create(
            address="1.1.1.1/32",
            status=self.status_active,
            vrf=vrf,
            assigned_object=Interface.objects.create(device=self.device_1, name="Loopback2"),
        )
        self.peergroup.validated_save()
        self.assertEqual(self.peergroup.vrf, vrf)

    def test_deleting_device_deletes_peergroup(self):
        """Deleting a Device should delete its associated PeerGroup(s)."""
        self.device_1.delete()
        with self.assertRaises(models.PeerGroup.DoesNotExist):
            self.peergroup.refresh_from_db()


class PeerEndpointTestCase(TestCase):
    """Test the PeerEndpoint model."""

    @classmethod
    def setUpTestData(cls):
        """One-time class data setup."""
        cls.status_active = Status.objects.get(slug="active")
        cls.status_active.content_types.add(ContentType.objects.get_for_model(models.PeerSession))
        manufacturer = Manufacturer.objects.create(name="Cisco", slug="cisco")
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model="CSR 1000V", slug="csr1000v")
        site = Site.objects.create(name="Site 1", slug="site-1")
        devicerole = DeviceRole.objects.create(name="Router", slug="router", color="ff0000")
        cls.device_1 = Device.objects.create(
            device_type=devicetype, device_role=devicerole, name="Device 1", site=site, status=cls.status_active
        )
        cls.interface_1 = Interface.objects.create(device=cls.device_1, name="Loopback1")
        cls.device_2 = Device.objects.create(
            device_type=devicetype, device_role=devicerole, name="Device 2", site=site, status=cls.status_active
        )
        cls.vrf = VRF.objects.create(name="Ark B")

        cls.peeringrole_internal = models.PeeringRole.objects.create(name="Internal", slug="internal", color="333333")

        cls.peergroup_1 = models.PeerGroup.objects.create(
            name="Peer Group A",
            device=cls.device_1,
            role=cls.peeringrole_internal,
            vrf=cls.vrf,
        )
        cls.peergroup_2 = models.PeerGroup.objects.create(
            name="Peer Group A",
            device=cls.device_2,
            role=cls.peeringrole_internal,
        )
        cls.ipaddress_2 = IPAddress.objects.create(
            address="1.1.1.2/32",
            vrf=cls.vrf,
            status=cls.status_active,
        )

    def setUp(self):
        """Per-test data setup."""
        self.ipaddress_1 = IPAddress.objects.create(
            address="1.1.1.1/32", vrf=self.vrf, status=self.status_active, assigned_object=self.interface_1
        )
        self.peerendpoint_1 = models.PeerEndpoint.objects.create(
            local_ip=self.ipaddress_1,
            peer_group=self.peergroup_1,
            vrf=self.vrf,
        )
        self.peerendpoint_1.clean()
        self.peerendpoint_2 = models.PeerEndpoint.objects.create(local_ip=self.ipaddress_2)
        self.peerendpoint_2.clean()

    def test_str(self):
        """Test string representation of a PeerEndpoint."""
        self.assertEqual(str(self.peerendpoint_1), "1.1.1.1/32 (unknown AS)")

    def test_vrf_fixup_from_local_ip(self):
        """If VRF is None, but local_ip is assigned to a VRF, use that."""
        self.peerendpoint_1.vrf = None
        self.peerendpoint_1.validated_save()
        self.assertEqual(self.peerendpoint_1.vrf, self.vrf)

    # TODO VRF fixup from router_id?

    def test_local_ip_vrf_mismatch(self):
        """Clean should fail if local_ip is assigned to a different VRF than the specified one."""
        self.peerendpoint_1.vrf = VRF.objects.create(name="Some other VRF")
        with self.assertRaises(ValidationError) as context:
            self.peerendpoint_1.validated_save()
        self.assertEqual(
            context.exception.messages[0],
            "VRF Some other VRF was specified, but one or more attributes refer instead to Ark B",
        )

    def test_peer_group_device_mismatch(self):
        """The specified peer-group must belong to the specified device if any."""
        self.peerendpoint_1.peer_group = self.peergroup_2
        with self.assertRaises(ValidationError) as context:
            self.peerendpoint_1.validated_save()
        self.assertIn(
            "Various attributes refer to different devices and/or virtual machines",
            context.exception.messages[0],
        )

    def test_peer_group_vrf_mismatch(self):
        """The specified peer-group must belong to the specified VRF if any."""
        self.peerendpoint_1.peer_group = models.PeerGroup.objects.create(
            device=self.device_1,
            name="Group B",
            role=self.peeringrole_internal,
            vrf=None,
        )
        with self.assertRaises(ValidationError) as context:
            self.peerendpoint_1.validated_save()
        self.assertIn(
            "Various attributes refer to different VRFs",
            context.exception.messages[0],
        )

    def test_deleting_ip_address_deletes_endpoint(self):
        """Deleting an IPAddress should delete the associated PeerEndpoint(s)."""
        self.ipaddress_1.delete()
        with self.assertRaises(models.PeerEndpoint.DoesNotExist):
            self.peerendpoint_1.refresh_from_db()

    def test_deleting_endpoint_deletes_session(self):
        """Deleting a PeerEndpoint should delete its associated PeerSession."""
        peersession = models.PeerSession.objects.create(role=self.peeringrole_internal, status=self.status_active)
        peersession.endpoints.set((self.peerendpoint_1, self.peerendpoint_2))
        self.peerendpoint_1.peer = self.peerendpoint_2
        self.peerendpoint_2.peer = self.peerendpoint_1
        self.peerendpoint_1.validated_save()
        self.peerendpoint_2.validated_save()
        self.assertEqual(self.peerendpoint_1.session, peersession)
        self.assertEqual(self.peerendpoint_2.session, peersession)

        self.peerendpoint_1.delete()
        with self.assertRaises(models.PeerSession.DoesNotExist):
            peersession.refresh_from_db()

        self.peerendpoint_2.refresh_from_db()
        self.assertIsNone(self.peerendpoint_2.peer)
        self.assertIsNone(self.peerendpoint_2.session)


class PeerSessionTestCase(TestCase):
    """Test the PeerSession model."""

    @classmethod
    def setUpTestData(cls):
        """One-time class data setup."""
        status_active = Status.objects.get(slug="active")
        status_active.content_types.add(ContentType.objects.get_for_model(models.PeerSession))

        address_1 = IPAddress.objects.create(address="1.1.1.1/32", status=status_active)
        address_2 = IPAddress.objects.create(address="2.2.2.2/32", status=status_active)

        endpoint_1 = models.PeerEndpoint.objects.create(local_ip=address_1)
        endpoint_2 = models.PeerEndpoint.objects.create(local_ip=address_2)

        peeringrole_internal = models.PeeringRole.objects.create(name="Internal", slug="internal", color="ffffff")

        cls.peersession = models.PeerSession.objects.create(status=status_active, role=peeringrole_internal)
        cls.peersession.endpoints.set([endpoint_1, endpoint_2])

    def test_str(self):
        """Test the string representation of a PeerSession."""
        self.assertEqual("1.1.1.1/32 (unknown AS) ↔︎ 2.2.2.2/32 (unknown AS)", str(self.peersession))


class AddressFamilyTestCase(TestCase):
    """Test the AddressFamily model."""

    @classmethod
    def setUpTestData(cls):
        """One-time class data setup."""
        cls.status_active = Status.objects.get(slug="active")
        manufacturer = Manufacturer.objects.create(name="Cisco", slug="cisco")
        cls.devicetype = DeviceType.objects.create(manufacturer=manufacturer, model="CSR 1000V", slug="csr1000v")
        cls.site = Site.objects.create(name="Site 1", slug="site-1")
        cls.devicerole = DeviceRole.objects.create(name="Router", slug="router", color="ff0000")

    def setUp(self):
        self.device = Device.objects.create(
            device_type=self.devicetype,
            device_role=self.devicerole,
            name="Device 1",
            site=self.site,
            status=self.status_active,
        )
        interface = Interface.objects.create(device=self.device, name="Loopback1")
        self.peeringrole_internal = models.PeeringRole.objects.create(name="Internal", slug="internal", color="333333")

        self.peergroup = models.PeerGroup.objects.create(
            name="Peer Group A",
            device=self.device,
            role=self.peeringrole_internal,
        )

        address = IPAddress.objects.create(address="1.1.1.1/32", status=self.status_active, assigned_object=interface)
        self.peerendpoint = models.PeerEndpoint.objects.create(local_ip=address)

        self.addressfamily_1 = models.AddressFamily.objects.create(
            afi_safi=AFISAFIChoices.AFI_IPV4,
            device=self.device,
        )
        self.addressfamily_2 = models.AddressFamily.objects.create(
            afi_safi=AFISAFIChoices.AFI_IPV4,
            device=self.device,
            peer_group=self.peergroup,
        )
        self.addressfamily_3 = models.AddressFamily.objects.create(
            afi_safi=AFISAFIChoices.AFI_IPV4,
            device=self.device,
            peer_endpoint=self.peerendpoint,
        )

    def test_str(self):
        """Test the string representation of an AddressFamily."""
        self.assertEqual("AFI-SAFI ipv4 on Device 1", str(self.addressfamily_1))
        self.assertEqual("AFI-SAFI ipv4 for Peer Group A on Device 1", str(self.addressfamily_2))
        self.assertEqual("AFI-SAFI ipv4 for 1.1.1.1/32 (unknown AS)", str(self.addressfamily_3))

    def test_peer_group_peer_endpoint_mutual_exclusion(self):
        addressfamily = models.AddressFamily(
            afi_safi=AFISAFIChoices.AFI_VPNV4,
            device=self.device,
            peer_group=self.peergroup,
            peer_endpoint=self.peerendpoint,
        )
        with self.assertRaises(ValidationError) as context:
            addressfamily.validated_save()
        self.assertIn(
            "An AddressFamily cannot reference both a peer-group and a peer endpoint",
            context.exception.messages[0],
        )

    def test_deleting_device_deletes_addressfamily(self):
        """Deleting a Device should delete its associated AddressFamily(s)."""
        self.device.delete()
        with self.assertRaises(models.AddressFamily.DoesNotExist):
            self.addressfamily_1.refresh_from_db()
        with self.assertRaises(models.AddressFamily.DoesNotExist):
            self.addressfamily_2.refresh_from_db()
        with self.assertRaises(models.AddressFamily.DoesNotExist):
            self.addressfamily_3.refresh_from_db()
