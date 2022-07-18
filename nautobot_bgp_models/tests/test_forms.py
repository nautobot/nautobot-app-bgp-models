"""Unit test automation for Form classes in nautobot_bgp_models."""

from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from nautobot.circuits.models import Provider
from nautobot.dcim.models import Device, DeviceRole, DeviceType, Interface, Manufacturer, Site
from nautobot.extras.models import Status
from nautobot.ipam.models import IPAddress

from nautobot_bgp_models import models, forms


class AutonomousSystemFormTestCase(TestCase):
    """Test the AutonomousSystem create/edit form."""

    form_class = forms.AutonomousSystemForm

    @classmethod
    def setUpTestData(cls):
        """Set up class-wide data for the test."""
        cls.status_active = Status.objects.get(slug="active")
        cls.status_active.content_types.add(ContentType.objects.get_for_model(models.AutonomousSystem))

    def test_valid_asn(self):
        data = {"asn": 1, "status": self.status_active}
        form = self.form_class(data)
        self.assertTrue(form.is_valid())
        self.assertTrue(form.save())

    def test_invalid_asn(self):
        data = {"asn": 0, "status": self.status_active}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual("Ensure this value is greater than or equal to 1.", form.errors["asn"][0])

        data = {"asn": 4294967296, "status": self.status_active}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual("Ensure this value is less than or equal to 4294967295.", form.errors["asn"][0])

    def test_status_required(self):
        data = {"asn": 4200000001}
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual("This field is required.", form.errors["status"][0])


class PeerGroupFormTestCase(TestCase):
    """Test the PeerGroup create/edit form."""

    form_class = forms.PeerGroupForm

    @classmethod
    def setUpTestData(cls):
        """Set up class-wide data for the test."""
        status_active = Status.objects.get(slug="active")

        manufacturer = Manufacturer.objects.create(name="Cisco", slug="cisco")
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model="CSR 1000V", slug="csr1000v")
        site = Site.objects.create(name="Site 1", slug="site-1")
        devicerole = DeviceRole.objects.create(name="Router", slug="router", color="ff0000")
        cls.device_1 = Device.objects.create(
            device_type=devicetype, device_role=devicerole, name="Device 1", site=site, status=status_active
        )
        cls.interface_1 = Interface.objects.create(device=cls.device_1, name="Loopback1")
        cls.ip = IPAddress.objects.create(address="1.1.1.2/32", status=status_active, assigned_object=cls.interface_1)

        # clustertype = ClusterType.objects.create(name="Cluster Type A", slug="cluster-type-a")
        # cluster = Cluster.objects.create(name="Cluster A", type=clustertype)
        # cls.virtualmachine_1 = VirtualMachine.objects.create(name="VM 1", cluster=cluster, status=status_active)
        # cls.vminterface_1 = VMInterface.objects.create(name="eth0", virtual_machine=cls.virtualmachine_1)

        cls.peeringrole_internal = models.PeeringRole.objects.create(name="Internal", slug="internal", color="333333")

        asn_1 = models.AutonomousSystem.objects.create(asn=4294967294, status=status_active)

        cls.bgp_routing_instance = models.BGPRoutingInstance.objects.create(
            description="Hello World!",
            autonomous_system=asn_1,
            device=cls.device_1,
        )

    def test_valid_form(self):
        """Device can be a Device."""
        data = {
            "name": "Peer Group A",
            "role": self.peeringrole_internal,
            "routing_instance": self.bgp_routing_instance,
        }
        form = self.form_class(data)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertTrue(form.save())

        peergroup = models.PeerGroup.objects.get(name="Peer Group A", routing_instance=self.bgp_routing_instance)
        self.assertEqual(peergroup.role, self.peeringrole_internal)

    def test_source_interface_cannot_be_both(self):
        """Update source cannot be both an Interface and an IP."""
        data = {
            "name": "Peer Group A",
            "role": self.peeringrole_internal,
            "routing_instance": self.bgp_routing_instance,
            "source_ip": self.ip,
            "source_interface": self.interface_1,
        }
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            "Can not set both IP and Update source options",
            form.errors["__all__"][0],
        )

    def test_source_interface(self):
        """Update source can be an Interface."""
        data = {
            "name": "Peer Group A",
            "role": self.peeringrole_internal,
            "routing_instance": self.bgp_routing_instance,
            "source_interface": self.interface_1,
        }
        form = self.form_class(data)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertTrue(form.save())

        peergroup = models.PeerGroup.objects.get(name="Peer Group A")
        self.assertEqual(peergroup.source_interface, self.interface_1)

    def test_source_ip(self):
        """Update source can be an Interface."""
        data = {
            "name": "Peer Group A",
            "role": self.peeringrole_internal,
            "routing_instance": self.bgp_routing_instance,
            "source_ip": self.ip,
        }
        form = self.form_class(data)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertTrue(form.save())

        peergroup = models.PeerGroup.objects.get(name="Peer Group A")
        self.assertEqual(peergroup.source_ip, self.ip)


# TODO Find a way to model alter_obj within the test case,
# Currently all tests are failing because the peering object is missing
class PeerEndpointFormTestCase(TestCase):
    """Test the PeerEndpoint create/edit form."""

    form_class = forms.PeerEndpointForm

    @classmethod
    def setUpTestData(cls):
        """Set up class-wide data for the test."""
        status_active = Status.objects.get(slug="active")
        manufacturer = Manufacturer.objects.create(name="Cisco", slug="cisco")
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model="CSR 1000V", slug="csr1000v")
        site = Site.objects.create(name="Site 1", slug="site-1")
        devicerole = DeviceRole.objects.create(name="Router", slug="router", color="ff0000")
        cls.device_1 = Device.objects.create(
            device_type=devicetype, device_role=devicerole, name="Device 1", site=site, status=status_active
        )
        cls.interface_1 = Interface.objects.create(device=cls.device_1, name="Loopback1")

        cls.address_1 = IPAddress.objects.create(
            address="1.1.1.1/32",
            status=status_active,
            assigned_object=cls.interface_1,
        )

        cls.address_2 = IPAddress.objects.create(
            address="1.1.1.2/32",
            status=status_active,
        )

        asn_1 = models.AutonomousSystem.objects.create(asn=4294967291, status=status_active)
        provider = Provider.objects.create(name="Provider", slug="provider")
        cls.asn_2 = models.AutonomousSystem.objects.create(asn=4294967292, status=status_active, provider=provider)

        cls.bgp_routing_instance = models.BGPRoutingInstance.objects.create(
            description="Hello World!",
            autonomous_system=asn_1,
            device=cls.device_1,
        )

        # clustertype = ClusterType.objects.create(name="Cluster Type A", slug="cluster-type-a")
        # cluster = Cluster.objects.create(name="Cluster A", type=clustertype)
        # cls.virtualmachine_1 = VirtualMachine.objects.create(name="VM 1", cluster=cluster, status=status_active)
        # cls.vminterface_1 = VMInterface.objects.create(name="eth0", virtual_machine=cls.virtualmachine_1)

        cls.peeringrole = models.PeeringRole.objects.create(name="Internal", slug="internal", color="333333")

        cls.peering = models.Peering.objects.create(
            status=status_active,
        )

        # cls.address_1 = IPAddress.objects.create(address="10.1.1.1/24", status=status_active)
        # cls.address_2 = IPAddress.objects.create(address="10.1.1.2/24", status=status_active)

        # cls.endpoint_1 = models.PeerEndpoint.objects.create(local_ip=cls.address_1, peering=cls.peering)

    def test_valid_form(self):
        """Device can be a Device."""
        data = {
            # "name": "Peer Group A",
            "role": self.peeringrole,
            "routing_instance": self.bgp_routing_instance,
            "source_ip": self.address_1,
            "peering": self.peering,
        }
        form = self.form_class(data)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertTrue(form.save())

        peerendpoint = models.PeerEndpoint.objects.get(routing_instance=self.bgp_routing_instance)
        self.assertEqual(peerendpoint.role, self.peeringrole)

    def test_source_interface_cannot_be_both(self):
        """Update source cannot be both an Interface and a VMInterface."""
        data = {
            "role": self.peeringrole,
            "routing_instance": self.bgp_routing_instance,
            "source_interface": self.interface_1,
            "source_ip": self.address_1,
            "peering": self.peering,
        }
        form = self.form_class(data)

        self.assertFalse(form.is_valid())
        self.assertEqual(
            "Can not set both IP and Update source options",
            form.errors["__all__"][0],
        )

    def test_set_peer(self):
        """Endpoint peer will should be populated when a second endpoint is added to a Peering."""
        data = {
            "role": self.peeringrole,
            "routing_instance": self.bgp_routing_instance,
            "source_ip": self.address_1,
            "peering": self.peering,
        }
        form = self.form_class(data)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertTrue(form.save())

        peerendpoint = models.PeerEndpoint.objects.get(routing_instance=self.bgp_routing_instance)

        data = {
            "source_ip": self.address_2,
            "autonomous_system": self.asn_2,
            "peering": self.peering,
        }

        form = self.form_class(data)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertTrue(form.save())

        peerendpoint.refresh_from_db()
        self.assertIsNotNone(peerendpoint.peer)


class AddressFamilyFormTestCase(TestCase):
    """Test the AddressFamily create/edit form."""

    form_class = forms.AddressFamilyForm

    @classmethod
    def setUpTestData(cls):
        """Set up class-wide data for the test."""
        status_active = Status.objects.get(slug="active")
        cls.address = IPAddress.objects.create(address="1.1.1.1/32", status=status_active)

        manufacturer = Manufacturer.objects.create(name="Cisco", slug="cisco")
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model="CSR 1000V", slug="csr1000v")
        site = Site.objects.create(name="Site 1", slug="site-1")
        devicerole = DeviceRole.objects.create(name="Router", slug="router", color="ff0000")
        cls.device_1 = Device.objects.create(
            device_type=devicetype, device_role=devicerole, name="Device 1", site=site, status=status_active
        )

        cls.asn_1 = models.AutonomousSystem.objects.create(asn=4294967292, status=status_active)

        cls.bgp_routing_instance = models.BGPRoutingInstance.objects.create(
            description="Hello World!",
            autonomous_system=cls.asn_1,
            device=cls.device_1,
        )

    def test_valid_form(self):
        """Valid AddressFamily form."""
        data = {
            "routing_instance": self.bgp_routing_instance,
            "afi_safi": "ipv4_unicast",
        }
        form = self.form_class(data)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertTrue(form.save())

        _af = models.AddressFamily.objects.get(routing_instance=self.bgp_routing_instance, afi_safi="ipv4_unicast")
        self.assertEqual(_af.afi_safi, "ipv4_unicast")
