"""Unit test automation for Form classes in nautobot_bgp_models."""

from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from nautobot.dcim.models import Device, DeviceRole, DeviceType, Interface, Manufacturer, Site
from nautobot.extras.models import Status
from nautobot.ipam.models import IPAddress
from nautobot.virtualization.models import Cluster, ClusterType, VirtualMachine, VMInterface

from nautobot_bgp_models import models, forms
from nautobot_bgp_models.choices import AFISAFIChoices


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

        clustertype = ClusterType.objects.create(name="Cluster Type A", slug="cluster-type-a")
        cluster = Cluster.objects.create(name="Cluster A", type=clustertype)
        cls.virtualmachine_1 = VirtualMachine.objects.create(name="VM 1", cluster=cluster, status=status_active)
        cls.vminterface_1 = VMInterface.objects.create(name="eth0", virtual_machine=cls.virtualmachine_1)

        cls.peeringrole_internal = models.PeeringRole.objects.create(name="Internal", slug="internal", color="333333")

    def test_device_cannot_be_both(self):
        """Device cannot be both a Device and a VirtualMachine."""
        data = {
            "name": "Peer Group A",
            "device_device": self.device_1,
            "device_virtualmachine": self.virtualmachine_1,
            "role": self.peeringrole_internal,
        }
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            "Cannot select both a device and a virtual machine as the parent device",
            form.errors["__all__"][0],
        )

    def test_device_device(self):
        """Device can be a Device."""
        data = {
            "name": "Peer Group A",
            "device_device": self.device_1,
            "role": self.peeringrole_internal,
        }
        form = self.form_class(data)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertTrue(form.save())

        peergroup = models.PeerGroup.objects.get(name="Peer Group A")
        self.assertEqual(peergroup.device, self.device_1)

    def test_device_virtualmachine(self):
        """Device can be a VirtualMachine."""
        data = {
            "name": "Peer Group A",
            "device_virtualmachine": self.virtualmachine_1,
            "role": self.peeringrole_internal,
        }
        form = self.form_class(data)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertTrue(form.save())

        peergroup = models.PeerGroup.objects.get(name="Peer Group A")
        self.assertEqual(peergroup.device, self.virtualmachine_1)

    def test_update_source_cannot_be_both(self):
        """Update source cannot be both an Interface and a VMInterface."""
        data = {
            "name": "Peer Group A",
            "device_device": self.device_1,
            "role": self.peeringrole_internal,
            "update_source_interface": self.interface_1,
            "update_source_vminterface": self.vminterface_1,
        }
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            "Cannot select both a device interface and a virtual machine interface as update-source",
            form.errors["__all__"][0],
        )

    def test_update_source_interface(self):
        """Update source can be an Interface."""
        data = {
            "name": "Peer Group A",
            "device_device": self.device_1,
            "role": self.peeringrole_internal,
            "update_source_interface": self.interface_1,
        }
        form = self.form_class(data)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertTrue(form.save())

        peergroup = models.PeerGroup.objects.get(name="Peer Group A")
        self.assertEqual(peergroup.update_source, self.interface_1)

    def test_update_source_vminterface(self):
        """Update source can be a VMInterface."""
        data = {
            "name": "Peer Group A",
            "device_virtualmachine": self.virtualmachine_1,
            "role": self.peeringrole_internal,
            "update_source_vminterface": self.vminterface_1,
        }
        form = self.form_class(data)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertTrue(form.save())

        peergroup = models.PeerGroup.objects.get(name="Peer Group A")
        self.assertEqual(peergroup.update_source, self.vminterface_1)


class PeerEndpointFormTestCase(TestCase):
    """Test the PeerEndpoint create/edit form."""

    form_class = forms.PeerEndpointForm

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
        cls.interface_1 = Interface.objects.create(device=cls.device_1, name="Loopback1")

        clustertype = ClusterType.objects.create(name="Cluster Type A", slug="cluster-type-a")
        cluster = Cluster.objects.create(name="Cluster A", type=clustertype)
        cls.virtualmachine_1 = VirtualMachine.objects.create(name="VM 1", cluster=cluster, status=status_active)
        cls.vminterface_1 = VMInterface.objects.create(name="eth0", virtual_machine=cls.virtualmachine_1)

        cls.peeringrole = models.PeeringRole.objects.create(name="Internal", slug="internal", color="333333")

        cls.session = models.PeerSession.objects.create(
            role=cls.peeringrole,
            status=status_active,
        )
        cls.address_1 = IPAddress.objects.create(address="10.1.1.1/24", status=status_active)
        cls.address_2 = IPAddress.objects.create(address="10.1.1.2/24", status=status_active)

        cls.endpoint_1 = models.PeerEndpoint.objects.create(local_ip=cls.address_1, session=cls.session)

    def test_update_source_cannot_be_both(self):
        """Update source cannot be both an Interface and a VMInterface."""
        data = {
            "local_ip": self.address.pk,
            "update_source_interface": self.interface_1,
            "update_source_vminterface": self.vminterface_1,
            "session": self.session.pk,
        }
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            "Cannot select both a device interface and a virtual machine interface as update-source",
            form.errors["__all__"][0],
        )

    def test_set_peer(self):
        """Endpoint peer will should be populated when a second endpoint is added to a PeerSession."""
        data = {
            "local_ip": self.address_2.pk,
            "session": self.session.pk,
        }

        form = self.form_class(data)
        self.assertTrue(form.is_valid())

        form.save()
        self.endpoint_1.refresh_from_db()
        self.assertIsNotNone(self.endpoint_1.peer)


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

        clustertype = ClusterType.objects.create(name="Cluster Type A", slug="cluster-type-a")
        cluster = Cluster.objects.create(name="Cluster A", type=clustertype)
        cls.virtualmachine_1 = VirtualMachine.objects.create(name="VM 1", cluster=cluster, status=status_active)

    def test_device_cannot_be_both(self):
        """Device cannot be both a Device and a VirtualMachine."""
        data = {
            "afi_safi": AFISAFIChoices.AFI_IPV4,
            "device_device": self.device_1.pk,
            "device_virtualmachine": self.virtualmachine_1.pk,
        }
        form = self.form_class(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            "Cannot select both a device and a virtual machine as the parent device",
            form.errors["__all__"][0],
        )
