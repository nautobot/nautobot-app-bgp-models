"""Unit test automation for Model classes in nautobot_bgp_models."""

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db.models.deletion import ProtectedError
from django.test import TestCase
from nautobot.circuits.models import Provider
from nautobot.dcim.models import Device, DeviceType, Interface, Location, LocationType, Manufacturer
from nautobot.extras.models import Role, Status
from nautobot.ipam.models import VRF, IPAddress, Namespace, Prefix
from nautobot.virtualization.models import Cluster, ClusterType, VirtualMachine, VMInterface

from nautobot_bgp_models import models
from nautobot_bgp_models.choices import AFISAFIChoices


class AutonomousSystemTestCase(TestCase):
    """Test the AutonomousSystem model."""

    @classmethod
    def setUpTestData(cls):
        """One-time class data setup."""
        status_active = Status.objects.get(name__iexact="active")
        status_active.content_types.add(ContentType.objects.get_for_model(models.AutonomousSystem))

        cls.autonomous_system = models.AutonomousSystem.objects.create(
            asn=15521, status=status_active, description="Hi ex Premium Internet AS!"
        )

        cls.autonomous_system_32_bit = models.AutonomousSystem.objects.create(
            asn=655460, status=status_active, description="Test Description"
        )

    def test_str(self):
        """Test string representation of an AutonomousSystem."""
        self.assertEqual(str(self.autonomous_system), "AS 15521")

    def test_asdot(self):
        """Test representation of an AutonomousSystem using asdot notation."""
        self.assertEqual(self.autonomous_system_32_bit.asn_asdot, "10.100")


class AutonomousSystemRangeTestCase(TestCase):
    """Test the AutonomousSystemRange model."""

    @classmethod
    def setUpTestData(cls):
        """One-time class data setup."""
        status_active = Status.objects.get(name__iexact="active")
        status_active.content_types.add(ContentType.objects.get_for_model(models.AutonomousSystem))

        cls.autonomous_system_100 = models.AutonomousSystem.objects.create(
            asn=100, status=status_active, description="AS100"
        )
        cls.autonomous_system_101 = models.AutonomousSystem.objects.create(
            asn=101, status=status_active, description="AS101"
        )
        cls.autonomous_system_120 = models.AutonomousSystem.objects.create(
            asn=120, status=status_active, description="AS120"
        )
        cls.autonomous_system_150 = models.AutonomousSystem.objects.create(
            asn=150, status=status_active, description="AS150"
        )
        cls.asn_range = models.AutonomousSystemRange.objects.create(
            name="Test Range", asn_min=100, asn_max=125, description="Test Range"
        )

    def test_str(self):
        """Test string representation of an AutonomousSystemRange."""
        self.assertEqual(str(self.asn_range), "ASN Range 100-125")

    def test_max_gt_min(self):
        with self.assertRaises(ValidationError) as context:
            self.asn_range.asn_min = 100
            self.asn_range.asn_max = 90
            self.asn_range.validated_save()
        self.assertIn(
            "asn_min value must be lower than asn_max value.",
            context.exception.messages[0],
        )


class BGPRoutingInstanceTestCase(TestCase):
    """Test the BGPRoutingInstance model."""

    @classmethod
    def setUpTestData(cls):
        """One-time class data setup."""
        cls.status_active = Status.objects.get(name__iexact="active")

        manufacturer = Manufacturer.objects.create(name="Cisco")
        cls.devicetype = DeviceType.objects.create(manufacturer=manufacturer, model="CSR 1000V")
        location_type = LocationType.objects.create(name="site")
        location_status = Status.objects.get_for_model(Location).first()
        cls.location = Location.objects.create(name="Site 1", location_type=location_type, status=location_status)
        cls.devicerole = Role.objects.create(name="Router", color="ff0000")
        cls.devicerole.content_types.add(ContentType.objects.get_for_model(Device))

    def setUp(self):
        """Per-test data setup."""
        self.device_1 = Device.objects.create(
            device_type=self.devicetype,
            role=self.devicerole,
            name="Device 1",
            location=self.location,
            status=self.status_active,
        )

        self.autonomous_system_8545 = models.AutonomousSystem.objects.create(
            asn=8545, status=self.status_active, description="Hi PL-IX AS! :-)"
        )

        self.bgp_routing_instance = models.BGPRoutingInstance.objects.create(
            description="Hello World!",
            autonomous_system=self.autonomous_system_8545,
            device=self.device_1,
            status=self.status_active,
        )

    def test_str(self):
        """Test string representation of a BGPRoutingInstance."""
        self.assertEqual(str(self.bgp_routing_instance), f"{self.device_1} - {self.autonomous_system_8545}")


class PeerGroupTestCase(TestCase):
    """Test the PeerGroup model."""

    @classmethod
    def setUpTestData(cls):
        """One-time class data setup."""
        status_active = Status.objects.get(name__iexact="active")

        manufacturer = Manufacturer.objects.create(name="Cisco")
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model="CSR 1000V")
        location_type = LocationType.objects.create(name="site")
        location_status = Status.objects.get_for_model(Location).first()
        location = Location.objects.create(name="Site 1", location_type=location_type, status=location_status)
        devicerole = Role.objects.create(name="Router", color="ff0000")
        devicerole.content_types.add(ContentType.objects.get_for_model(Device))

        cls.device_1 = Device.objects.create(
            device_type=devicetype,
            role=devicerole,
            name="Device 1",
            location=location,
            status=status_active,
        )

        autonomous_system_5616 = models.AutonomousSystem.objects.create(
            asn=5616, status=status_active, description="Hi ex Mediatel AS!"
        )

        cls.bgp_routing_instance = models.BGPRoutingInstance.objects.create(
            description="Hello World!",
            autonomous_system=autonomous_system_5616,
            device=cls.device_1,
            status=status_active,
        )

    def setUp(self):
        """Per-test data setup."""
        self.peergroup = models.PeerGroup.objects.create(
            name="Peer Group A", routing_instance=self.bgp_routing_instance
        )

    def test_str(self):
        """Test string representation of a PeerGroup."""
        self.assertEqual(str(self.peergroup), f"{self.peergroup.name} - {self.device_1.name}")

    # def test_vrf_fixup_from_router_id(self):
    #     """If VRF is None, but the router-id references a VRF, use that."""
    #     vrf = VRF.objects.create(name="red")
    #     self.peergroup.router_id = IPAddress.objects.create(
    #         address="1.1.1.1/32",
    #         status=self.status_active,
    #         vrf=vrf,
    #         assigned_object=Interface.objects.create(device=self.device_1, name="Loopback2"),
    #     )
    #     self.peergroup.validated_save()
    #     self.assertEqual(self.peergroup.vrf, vrf)


class PeerEndpointTestCase(TestCase):
    """Test the PeerEndpoint model."""

    @classmethod
    def setUpTestData(cls):  # pylint: disable=too-many-locals
        """One-time class data setup."""
        status_active = Status.objects.get(name__iexact="active")
        status_active.content_types.add(ContentType.objects.get_for_model(models.Peering))
        cls.status_active = status_active

        manufacturer = Manufacturer.objects.create(name="Cisco")
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model="CSR 1000V")
        location_type = LocationType.objects.create(name="site")
        location_status = Status.objects.get_for_model(Location).first()
        location = Location.objects.create(name="Site 1", location_type=location_type, status=location_status)
        devicerole = Role.objects.create(name="Router", color="ff0000")
        devicerole.content_types.add(ContentType.objects.get_for_model(Device))
        device_1 = Device.objects.create(
            device_type=devicetype, role=devicerole, name="Device 1", location=location, status=cls.status_active
        )
        interface_status = Status.objects.get_for_model(Interface).first()
        cls.interface_1 = Interface.objects.create(device=device_1, name="Loopback1", status=interface_status)
        device_2 = Device.objects.create(
            device_type=devicetype, role=devicerole, name="Device 2", location=location, status=cls.status_active
        )
        cls.interface_2 = Interface.objects.create(device=device_2, name="Loopback1", status=interface_status)

        cls.peeringrole_internal = Role.objects.create(name="Internal", color="333333")
        cls.peeringrole_internal.content_types.add(ContentType.objects.get_for_model(models.PeerGroup))

        autonomous_system_12345 = models.AutonomousSystem.objects.create(
            asn=12345, status=status_active, description="ASN 12345"
        )

        provider = Provider.objects.create(name="Provider")
        cls.autonomous_system_23456 = models.AutonomousSystem.objects.create(
            asn=23456,
            status=status_active,
            description="ASN 23456",
            provider=provider,
        )

        bgp_routing_instance_1 = models.BGPRoutingInstance.objects.create(
            description="BGP Routing Instance for device 1",
            autonomous_system=autonomous_system_12345,
            device=device_1,
            status=status_active,
        )
        cls.bgp_routing_instance_1 = bgp_routing_instance_1

        bgp_routing_instance_2 = models.BGPRoutingInstance.objects.create(
            description="BGP Routing Instance for device 2",
            autonomous_system=autonomous_system_12345,
            device=device_2,
            status=status_active,
        )
        cls.bgp_routing_instance_2 = bgp_routing_instance_2

        cls.peergroup_1 = models.PeerGroup.objects.create(
            name="Peer Group A",
            role=cls.peeringrole_internal,
            routing_instance=bgp_routing_instance_1,
        )
        cls.peergroup_2 = models.PeerGroup.objects.create(
            name="Peer Group A",
            role=cls.peeringrole_internal,
            routing_instance=bgp_routing_instance_2,
        )

        cls.namespace = Namespace.objects.first()
        prefix_status = Status.objects.get_for_model(Prefix).first()
        Prefix.objects.create(prefix="1.0.0.0/8", namespace=cls.namespace, status=prefix_status)

        cls.ipaddress_2 = IPAddress.objects.create(
            address="1.1.1.2/32",
            status=status_active,
            namespace=cls.namespace,
        )
        vm_cluster_type = ClusterType.objects.create(name="vShpere")
        vm_cluster = Cluster.objects.create(name="VM Test Cluster", cluster_type=vm_cluster_type)
        cls.virtual_machine_1 = VirtualMachine.objects.create(name="VM 1", cluster=vm_cluster, status=cls.status_active)
        cls.vm_interface_1 = VMInterface.objects.create(
            name="Loopback1", virtual_machine=cls.virtual_machine_1, status=status_active
        )

    def setUp(self):
        """Per-test data setup."""

        self.peering = models.Peering.objects.create(status=self.status_active)

        self.ipaddress_1 = IPAddress.objects.create(
            address="1.1.1.1/32",
            status=self.status_active,
            namespace=self.namespace,
        )

        self.interface_1.add_ip_addresses(self.ipaddress_1)

        self.peerendpoint_1 = models.PeerEndpoint.objects.create(
            source_ip=self.ipaddress_1,
            peer_group=self.peergroup_1,
            peering=self.peering,
            routing_instance=self.bgp_routing_instance_1,
        )
        self.peerendpoint_1.clean()
        self.peerendpoint_2 = models.PeerEndpoint.objects.create(
            source_ip=self.ipaddress_2, autonomous_system=self.autonomous_system_23456, peering=self.peering
        )
        self.peerendpoint_2.clean()

    def test_str(self):
        """Test string representation of a PeerEndpoint."""
        self.assertEqual(str(self.peerendpoint_1), "Device 1 1.1.1.1/32 (AS 12345)")
        self.assertEqual(str(self.peerendpoint_2), "1.1.1.2/32 (AS 23456)")

    # def test_vrf_fixup_from_local_ip(self):
    #     """If VRF is None, but local_ip is assigned to a VRF, use that."""
    #     self.peerendpoint_1.vrf = None
    #     self.peerendpoint_1.validated_save()
    #     self.assertEqual(self.peerendpoint_1.vrf, self.vrf)
    #
    # # TODO VRF fixup from router_id?
    #
    # def test_local_ip_vrf_mismatch(self):
    #     """Clean should fail if local_ip is assigned to a different VRF than the specified one."""
    #     self.peerendpoint_1.vrf = VRF.objects.create(name="Some other VRF")
    #     with self.assertRaises(ValidationError) as context:
    #         self.peerendpoint_1.validated_save()
    #     self.assertEqual(
    #         context.exception.messages[0],
    #         "VRF Some other VRF was specified, but one or more attributes refer instead to Ark B",
    #     )
    #
    # def test_peer_group_vrf_mismatch(self):
    #     """The specified peer-group must belong to the specified VRF if any."""
    #     self.peerendpoint_1.peer_group = models.PeerGroup.objects.create(
    #         name="Group B",
    #         role=self.peeringrole_internal,
    #         vrf=None,
    #     )
    #     with self.assertRaises(ValidationError) as context:
    #         self.peerendpoint_1.validated_save()
    #     self.assertIn(
    #         "Various attributes refer to different VRFs",
    #         context.exception.messages[0],
    #     )

    def test_deleting_ip_address_protects_endpoint(self):
        """Deleting an IPAddress should protect the associated PeerEndpoint(s)."""
        with self.assertRaises(ProtectedError):
            self.ipaddress_1.delete()

    def test_mandatory_asn(self):
        """PeerEndpoint should always have some ASN."""
        self.peerendpoint_2.autonomous_system = None
        self.peerendpoint_2.save()

        with self.assertRaises(ValidationError):
            self.peerendpoint_2.clean()

    def test_deleting_peering_deletes_endpoints(self):
        """Deleting a Peering should delete its associated PeerEndpoints."""
        self.peering.delete()

        with self.assertRaises(models.Peering.DoesNotExist):
            self.peering.refresh_from_db()

        with self.assertRaises(models.PeerEndpoint.DoesNotExist):
            self.peerendpoint_1.refresh_from_db()
            self.peerendpoint_2.refresh_from_db()

    def test_route_instance_matches_interface(self):
        """PeerEndpoint Routing Instance matches interface.device if assigned."""
        self.interface_1.ip_addresses.add(self.ipaddress_1)
        # assignement to secondary device should be ingored in Routing Instance validation
        self.interface_2.ip_addresses.add(self.ipaddress_1)
        self.peerendpoint_1.routing_instance = self.bgp_routing_instance_1
        self.peerendpoint_1.source_address = self.ipaddress_1
        self.peerendpoint_1.validated_save()

        self.interface_1.ip_addresses.remove(self.ipaddress_1)
        with self.assertRaises(ValidationError):
            self.peerendpoint_1.clean()

    def test_route_instance_duplicate_assignment(self):
        """PeerEndpoint not require Routing Instance for any Interface associations if ASN is provided."""
        self.interface_1.ip_addresses.add(self.ipaddress_1)
        self.interface_2.ip_addresses.add(self.ipaddress_1)
        self.peerendpoint_1.routing_instance = None
        self.peerendpoint_1.source_address = self.ipaddress_1
        self.peerendpoint_1.autonomous_system = self.autonomous_system_23456
        self.peerendpoint_1.validated_save()

        self.peerendpoint_1.autonomous_system = None
        with self.assertRaises(ValidationError):
            self.peerendpoint_1.clean()

    def test_route_instance_vm_interface(self):
        """PeerEndpoint not require Routing Instance for VMInterface association if ASN is provided."""
        self.vm_interface_1.ip_addresses.add(self.ipaddress_1)
        self.peerendpoint_1.routing_instance = None
        self.peerendpoint_1.source_address = self.ipaddress_1
        self.peerendpoint_1.autonomous_system = self.autonomous_system_23456
        self.peerendpoint_1.validated_save()

        self.peerendpoint_1.autonomous_system = None
        with self.assertRaises(ValidationError):
            self.peerendpoint_1.clean()


class PeeringTestCase(TestCase):
    """Test the Peering model."""

    @classmethod
    def setUpTestData(cls):
        """One-time class data setup."""
        status_active = Status.objects.get(name__iexact="active")
        status_active.content_types.add(ContentType.objects.get_for_model(models.Peering))

        # peeringrole_internal = models.PeeringRole.objects.create(name="Internal", slug="internal", color="ffffff")

        provider = Provider.objects.create(name="Provider")
        cls.autonomous_system_12345 = models.AutonomousSystem.objects.create(
            asn=12345,
            status=status_active,
            description="ASN 12345",
            provider=provider,
        )
        cls.autonomous_system_23456 = models.AutonomousSystem.objects.create(
            asn=23456,
            status=status_active,
            description="ASN 23456",
            provider=provider,
        )

        cls.peering = models.Peering.objects.create(status=status_active)

        namespace = Namespace.objects.first()
        prefix_status = Status.objects.get_for_model(Prefix).first()
        Prefix.objects.create(prefix="1.0.0.0/8", namespace=namespace, status=prefix_status)
        Prefix.objects.create(prefix="2.0.0.0/8", namespace=namespace, status=prefix_status)

        address_1 = IPAddress.objects.create(address="1.1.1.1/32", status=status_active, namespace=namespace)
        address_2 = IPAddress.objects.create(address="2.2.2.2/32", status=status_active, namespace=namespace)
        models.PeerEndpoint.objects.create(
            source_ip=address_1,
            peering=cls.peering,
            autonomous_system=cls.autonomous_system_12345,
        )
        models.PeerEndpoint.objects.create(
            source_ip=address_2,
            peering=cls.peering,
            autonomous_system=cls.autonomous_system_23456,
        )

    def test_str(self):
        """Test the string representation of a Peering."""
        self.assertTrue(
            str(self.peering)
            in ["2.2.2.2/32 (AS 23456) ↔︎ 1.1.1.1/32 (AS 12345)", "1.1.1.1/32 (AS 12345) ↔︎ 2.2.2.2/32 (AS 23456)"]
        )

    def test_update_peers(self):
        """Test update_peers to update peer on both endpoints."""
        endpoints = self.peering.endpoints.all()
        endpoint_a = endpoints[0]
        endpoint_z = endpoints[1]
        self.assertIsNone(endpoint_a.peer)
        self.assertIsNone(endpoint_z.peer)

        self.assertTrue(self.peering.update_peers())
        endpoint_a.refresh_from_db()
        endpoint_z.refresh_from_db()
        self.assertEqual(endpoint_a.peer, endpoint_z)
        self.assertEqual(endpoint_z.peer, endpoint_a)
        self.assertFalse(self.peering.update_peers())

        endpoint_a.delete()
        endpoint_z.refresh_from_db()
        self.peering.refresh_from_db()
        self.assertIsNone(self.peering.update_peers())

        endpoint_z.delete()
        self.peering.refresh_from_db()
        self.assertIsNone(self.peering.update_peers())


class AddressFamilyTestCase(TestCase):
    """Test the AddressFamily model."""

    @classmethod
    def setUpTestData(cls):
        """One-time class data setup."""
        cls.status_active = Status.objects.get(name__iexact="active")
        manufacturer = Manufacturer.objects.create(name="Cisco")
        cls.devicetype = DeviceType.objects.create(manufacturer=manufacturer, model="CSR 1000V")
        location_type = LocationType.objects.create(name="site")
        location_status = Status.objects.get_for_model(Location).first()
        cls.location = Location.objects.create(name="Site 1", location_type=location_type, status=location_status)
        cls.devicerole = Role.objects.create(name="Router", color="ff0000")
        cls.devicerole.content_types.add(ContentType.objects.get_for_model(Device))
        cls.vrf = VRF.objects.create(name="global")

    def setUp(self):
        self.device = Device.objects.create(
            device_type=self.devicetype,
            role=self.devicerole,
            name="Device 1",
            location=self.location,
            status=self.status_active,
        )

        self.autonomous_system_12345 = models.AutonomousSystem.objects.create(
            asn=123456,
            status=self.status_active,
            description="ASN 23456",
        )

        self.bgp_routing_instance_1 = models.BGPRoutingInstance.objects.create(
            description="BGP Routing Instance for device 1",
            autonomous_system=self.autonomous_system_12345,
            device=self.device,
            status=self.status_active,
        )

        # interface = Interface.objects.create(device=self.device, name="Loopback1")
        self.peeringrole_internal = Role.objects.create(name="Internal", color="333333")
        self.peeringrole_internal.content_types.add(ContentType.objects.get_for_model(models.PeerGroup))

        # self.peergroup = models.PeerGroup.objects.create(
        #     name="Peer Group A",
        #     role=self.peeringrole_internal,
        # )

        # peering = models.Peering.objects.create(status=self.status_active)
        # address = IPAddress.objects.create(address="1.1.1.1/32", status=self.status_active, assigned_object=interface)
        # self.peerendpoint = models.PeerEndpoint.objects.create(local_ip=address, peering=peering)

        self.addressfamily_1 = models.AddressFamily.objects.create(
            afi_safi=AFISAFIChoices.AFI_IPV4_UNICAST,
            routing_instance=self.bgp_routing_instance_1,
        )
        self.addressfamily_2 = models.AddressFamily.objects.create(
            afi_safi=AFISAFIChoices.AFI_IPV4_UNICAST,
            routing_instance=self.bgp_routing_instance_1,
            vrf=self.vrf,
        )
        # self.addressfamily_3 = models.AddressFamily.objects.create(
        #     afi_safi=AFISAFIChoices.AFI_IPV4_UNICAST,
        #     routing_instance=self.bgp_routing_instance_1,
        # )

    def test_str(self):
        """Test the string representation of an AddressFamily."""
        self.assertEqual("ipv4_unicast AF - Device 1", str(self.addressfamily_1))
        self.assertEqual("ipv4_unicast AF (VRF Global: (global)) Device 1", str(self.addressfamily_2))


#     def test_peer_group_peer_endpoint_mutual_exclusion(self):
#         addressfamily = models.AddressFamily(
#             afi_safi=AFISAFIChoices.AFI_VPNV4,
#             peer_group=self.peergroup,
#             peer_endpoint=self.peerendpoint,
#         )
#         with self.assertRaises(ValidationError) as context:
#             addressfamily.validated_save()
#         self.assertIn(
#             "An AddressFamily cannot reference both a peer-group and a peer endpoint",
#             context.exception.messages[0],
#         )
