"""Unit tests for table columns in nautobot_bgp_models."""

from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse
from nautobot.circuits.models import Provider
from nautobot.dcim.models import Device, DeviceType, Interface, Location, LocationType, Manufacturer
from nautobot.extras.models import Role, Status
from nautobot.ipam.models import IPAddress, Namespace, Prefix

from nautobot_bgp_models import models
from nautobot_bgp_models.table_columns import (
    AASNColumn,
    ADeviceColumn,
    AEndpointIPColumn,
    AProviderColumn,
    ZASNColumn,
    ZDeviceColumn,
    ZEndpointIPColumn,
    ZProviderColumn,
)


class MockRecord:
    """Mock record class for testing table columns."""

    def __init__(self, endpoint_a=None, endpoint_z=None):
        """Initialize mock record."""
        self.endpoint_a = endpoint_a
        self.endpoint_z = endpoint_z


class BaseTableColumnTestCase(TestCase):
    """Base test case for table columns with common setup."""

    @classmethod
    def setUpTestData(cls):
        """Set up test data for table column tests."""
        cls._create_base_objects()
        cls._create_devices_and_infrastructure()
        cls._create_asn_and_routing_instances()
        cls._create_peerings_with_endpoints()

    @classmethod
    def _create_base_objects(cls):
        """Create basic objects needed for testing."""
        # Create active status and assign to models
        cls.status_active = Status.objects.get(name__iexact="active")
        cls.status_active.content_types.add(ContentType.objects.get_for_model(models.AutonomousSystem))
        cls.status_active.content_types.add(ContentType.objects.get_for_model(models.BGPRoutingInstance))
        cls.status_active.content_types.add(ContentType.objects.get_for_model(models.Peering))

        # Create location infrastructure
        cls.location_type = LocationType.objects.create(name="Test Location Type")
        location_status = Status.objects.get_for_model(Location).first()
        cls.location = Location.objects.create(
            name="Test Location", location_type=cls.location_type, status=location_status
        )

        # Create device infrastructure
        cls.manufacturer = Manufacturer.objects.create(name="Test Manufacturer")
        cls.device_type = DeviceType.objects.create(manufacturer=cls.manufacturer, model="Test Device Type")
        cls.device_role = Role.objects.create(name="Router", color="ff0000")
        cls.device_role.content_types.add(ContentType.objects.get_for_model(Device))

    @classmethod
    def _create_devices_and_infrastructure(cls):
        """Create devices, providers, interfaces, and IP addresses."""
        # Create devices
        cls.device_a = Device.objects.create(
            name="Device A",
            location=cls.location,
            device_type=cls.device_type,
            role=cls.device_role,
            status=cls.status_active,
        )
        cls.device_b = Device.objects.create(
            name="Device B",
            location=cls.location,
            device_type=cls.device_type,
            role=cls.device_role,
            status=cls.status_active,
        )
        cls.device_c = Device.objects.create(
            name="Device C",
            location=cls.location,
            device_type=cls.device_type,
            role=cls.device_role,
            status=cls.status_active,
        )
        cls.device_z = Device.objects.create(
            name="Device Z",
            location=cls.location,
            device_type=cls.device_type,
            role=cls.device_role,
            status=cls.status_active,
        )

        # Create providers
        cls.provider_a = Provider.objects.create(name="Provider A")
        cls.provider_b = Provider.objects.create(name="AAA Provider")  # Sorts first alphabetically
        cls.provider_c = Provider.objects.create(name="ZZZ Provider")  # Sorts last alphabetically
        cls.provider_z = Provider.objects.create(name="Provider Z")

        # Create interfaces
        cls.interface_a = Interface.objects.create(
            device=cls.device_a, name="eth0", type="1000base-t", status=cls.status_active
        )
        cls.interface_b = Interface.objects.create(
            device=cls.device_b, name="eth0", type="1000base-t", status=cls.status_active
        )
        cls.interface_c = Interface.objects.create(
            device=cls.device_c, name="eth0", type="1000base-t", status=cls.status_active
        )
        cls.interface_z = Interface.objects.create(
            device=cls.device_z, name="eth0", type="1000base-t", status=cls.status_active
        )

        # Create IP infrastructure
        cls.namespace = Namespace.objects.create(name="Test Namespace")
        cls.prefix = Prefix.objects.create(prefix="192.168.1.0/24", namespace=cls.namespace, status=cls.status_active)

        # Create and assign IP addresses
        cls.ip_a = IPAddress.objects.create(address="192.168.1.1/24", namespace=cls.namespace, status=cls.status_active)
        cls.ip_b = IPAddress.objects.create(address="192.168.1.3/24", namespace=cls.namespace, status=cls.status_active)
        cls.ip_c = IPAddress.objects.create(address="192.168.1.4/24", namespace=cls.namespace, status=cls.status_active)
        cls.ip_z = IPAddress.objects.create(address="192.168.1.2/24", namespace=cls.namespace, status=cls.status_active)

        # Assign IP addresses to interfaces
        cls.ip_a.assigned_object = cls.interface_a
        cls.ip_a.save()
        cls.ip_b.assigned_object = cls.interface_b
        cls.ip_b.save()
        cls.ip_c.assigned_object = cls.interface_c
        cls.ip_c.save()
        cls.ip_z.assigned_object = cls.interface_z
        cls.ip_z.save()

    @classmethod
    def _create_asn_and_routing_instances(cls):
        """Create autonomous systems and BGP routing instances."""
        # Create autonomous systems with varied ASNs and providers
        cls.asn_a = models.AutonomousSystem.objects.create(
            asn=65001, status=cls.status_active, provider=cls.provider_a, description="ASN A"
        )
        cls.asn_b = models.AutonomousSystem.objects.create(
            asn=60000, status=cls.status_active, provider=cls.provider_b, description="ASN B (60000)"
        )
        cls.asn_c = models.AutonomousSystem.objects.create(
            asn=70000, status=cls.status_active, provider=cls.provider_c, description="ASN C (70000)"
        )
        cls.asn_z = models.AutonomousSystem.objects.create(
            asn=65002, status=cls.status_active, provider=cls.provider_z, description="ASN Z"
        )

        # Create BGP routing instances
        cls.routing_instance_a = models.BGPRoutingInstance.objects.create(
            device=cls.device_a,
            autonomous_system=cls.asn_a,
            status=cls.status_active,
        )
        cls.routing_instance_b = models.BGPRoutingInstance.objects.create(
            device=cls.device_b,
            autonomous_system=cls.asn_b,
            status=cls.status_active,
        )
        cls.routing_instance_c = models.BGPRoutingInstance.objects.create(
            device=cls.device_c,
            autonomous_system=cls.asn_c,
            status=cls.status_active,
        )
        cls.routing_instance_z = models.BGPRoutingInstance.objects.create(
            device=cls.device_z,
            autonomous_system=cls.asn_z,
            status=cls.status_active,
        )

    @classmethod
    def _create_peerings_with_endpoints(cls):
        """Create peerings with explicit A/Z side assignments using PK control."""
        # A/Z assignment is based on PK ordering (lowest PK = A, highest PK = Z)
        # Using explicit PKs ensures predictable and testable A/Z assignments

        # Peering 1: A=Device A (ASN 65001, Provider A), Z=Device Z (ASN 65002, Provider Z)
        cls.peering_1 = models.Peering.objects.create(status=cls.status_active)
        cls.peer_endpoint_a = models.PeerEndpoint(
            pk=1001,
            routing_instance=cls.routing_instance_a,
            source_interface=cls.interface_a,
            source_ip=cls.ip_a,
            peering=cls.peering_1,
        )
        cls.peer_endpoint_a.save(force_insert=True)
        cls.peer_endpoint_z = models.PeerEndpoint(
            pk=1002,
            routing_instance=cls.routing_instance_z,
            source_interface=cls.interface_z,
            source_ip=cls.ip_z,
            peering=cls.peering_1,
        )
        cls.peer_endpoint_z.save(force_insert=True)

        # Peering 2: A=Device B (ASN 60000, AAA Provider), Z=Device C (ASN 70000, ZZZ Provider)
        cls.peering_2 = models.Peering.objects.create(status=cls.status_active)
        endpoint_2a = models.PeerEndpoint(
            pk=2001,
            routing_instance=cls.routing_instance_b,
            source_interface=cls.interface_b,
            source_ip=cls.ip_b,
            peering=cls.peering_2,
        )
        endpoint_2a.save(force_insert=True)
        endpoint_2z = models.PeerEndpoint(
            pk=2002,
            routing_instance=cls.routing_instance_c,
            source_interface=cls.interface_c,
            source_ip=cls.ip_c,
            peering=cls.peering_2,
        )
        endpoint_2z.save(force_insert=True)

        # Peering 3: A=Device C (ASN 70000, ZZZ Provider), Z=Device A (ASN 65001, Provider A)
        cls.peering_3 = models.Peering.objects.create(status=cls.status_active)
        endpoint_3a = models.PeerEndpoint(pk=3001, routing_instance=cls.routing_instance_c, peering=cls.peering_3)
        endpoint_3a.save(force_insert=True)
        endpoint_3z = models.PeerEndpoint(pk=3002, routing_instance=cls.routing_instance_a, peering=cls.peering_3)
        endpoint_3z.save(force_insert=True)

        # Peering 4: A=Device Z (ASN 65002, Provider Z), Z=Device B (ASN 60000, AAA Provider)
        cls.peering_4 = models.Peering.objects.create(status=cls.status_active)
        endpoint_4a = models.PeerEndpoint(pk=4001, routing_instance=cls.routing_instance_z, peering=cls.peering_4)
        endpoint_4a.save(force_insert=True)
        endpoint_4z = models.PeerEndpoint(pk=4002, routing_instance=cls.routing_instance_b, peering=cls.peering_4)
        endpoint_4z.save(force_insert=True)

        # PREDICTABLE SORT ORDERS FOR TESTING:
        # Our 4 peerings with explicit A/Z assignments:
        # Peering 1: A=Device A (ASN 65001, Provider A),     Z=Device Z (ASN 65002, Provider Z)
        # Peering 2: A=Device B (ASN 60000, AAA Provider),   Z=Device C (ASN 70000, ZZZ Provider)
        # Peering 3: A=Device C (ASN 70000, ZZZ Provider),   Z=Device A (ASN 65001, Provider A)
        # Peering 4: A=Device Z (ASN 65002, Provider Z),     Z=Device B (ASN 60000, AAA Provider)
        #
        # A-side ascending order by ASN:    60000, 65001, 65002, 70000 → Peerings: 2, 1, 4, 3
        # A-side ascending order by Device: A, B, C, Z                 → Peerings: 1, 2, 3, 4
        # A-side ascending order by Provider: AAA, Provider A, Provider Z, ZZZ → Peerings: 2, 1, 4, 3
        #
        # Z-side ascending order by ASN:    60000, 65001, 65002, 70000 → Peerings: 4, 3, 1, 2
        # Z-side ascending order by Device: A, B, C, Z                 → Peerings: 3, 4, 2, 1
        # Z-side ascending order by Provider: AAA, Provider A, Provider Z, ZZZ → Peerings: 4, 3, 1, 2


class ADeviceColumnTestCase(BaseTableColumnTestCase):
    """Test cases for ADeviceColumn."""

    def setUp(self):
        """Set up test data."""
        self.column = ADeviceColumn()

    def test_render_with_device(self):
        """Test rendering when endpoint A has a device."""
        record = MockRecord(endpoint_a=self.peer_endpoint_a)
        result = self.column.render(record)

        # hyperlinked_object produces rich output with proper URL and device name
        expected_url = self.device_a.get_absolute_url()
        self.assertIn(f'href="{expected_url}"', result)
        self.assertIn("Device A", result)

    def test_render_without_device(self):
        """Test rendering when endpoint A has no device."""
        record = MockRecord(endpoint_a=None)
        result = self.column.render(record)
        self.assertIsNone(result)

    def test_render_without_routing_instance(self):
        """Test rendering when endpoint A has no routing instance."""
        endpoint_without_ri = models.PeerEndpoint.objects.create(peering=self.peering_1)
        record = MockRecord(endpoint_a=endpoint_without_ri)
        result = self.column.render(record)
        self.assertIsNone(result)

    def test_order_ascending(self):
        """Test ordering in ascending order."""
        queryset = models.Peering.objects.all()
        ordered_queryset, is_ordered = self.column.order(queryset, False)
        self.assertTrue(is_ordered)

        # Verify the annotation was added
        results = list(ordered_queryset)
        self.assertTrue(hasattr(results[0], "a_device_name"))

        # Verify exact sort order (A-side devices: A, B, C, Z)
        device_names = [getattr(result, "a_device_name") for result in results]
        expected_order = ["Device A", "Device B", "Device C", "Device Z"]
        self.assertEqual(device_names, expected_order)

    def test_order_descending(self):
        """Test ordering in descending order."""
        queryset = models.Peering.objects.all()
        ordered_queryset, is_ordered = self.column.order(queryset, True)
        self.assertTrue(is_ordered)

        # Verify the annotation was added
        results = list(ordered_queryset)
        self.assertTrue(hasattr(results[0], "a_device_name"))

        # Verify exact sort order (A-side devices: Z, C, B, A)
        device_names = [getattr(result, "a_device_name") for result in results]
        expected_order = ["Device Z", "Device C", "Device B", "Device A"]
        self.assertEqual(device_names, expected_order)


class ZDeviceColumnTestCase(BaseTableColumnTestCase):
    """Test cases for ZDeviceColumn."""

    def setUp(self):
        """Set up test data."""
        self.column = ZDeviceColumn()

    def test_render_with_device(self):
        """Test rendering when endpoint Z has a device."""
        record = MockRecord(endpoint_z=self.peer_endpoint_z)
        result = self.column.render(record)

        # hyperlinked_object produces rich output with proper URL and device name
        expected_url = self.device_z.get_absolute_url()
        self.assertIn(f'href="{expected_url}"', result)
        self.assertIn("Device Z", result)

    def test_render_without_device(self):
        """Test rendering when endpoint Z has no device."""
        record = MockRecord(endpoint_z=None)
        result = self.column.render(record)
        self.assertIsNone(result)

    def test_order_ascending(self):
        """Test ordering in ascending order."""
        queryset = models.Peering.objects.all()
        _, is_ordered = self.column.order(queryset, False)
        self.assertTrue(is_ordered)

    def test_order_descending(self):
        """Test ordering in descending order."""
        queryset = models.Peering.objects.all()
        ordered_queryset, is_ordered = self.column.order(queryset, True)
        self.assertTrue(is_ordered)

        # Verify exact sort order (Z-side devices: Z, C, B, A)
        results = list(ordered_queryset)
        device_names = [getattr(result, "z_device_name") for result in results]
        expected_order = ["Device Z", "Device C", "Device B", "Device A"]
        self.assertEqual(device_names, expected_order)


class AEndpointIPColumnTestCase(BaseTableColumnTestCase):
    """Test cases for AEndpointIPColumn."""

    def setUp(self):
        """Set up test data."""
        self.column = AEndpointIPColumn()

    def test_render_with_ip(self):
        """Test rendering when endpoint A has an IP address."""
        record = MockRecord(endpoint_a=self.peer_endpoint_a)
        result = self.column.render(record)

        # hyperlinked_object produces richer output with device and ASN info
        expected_url = self.peer_endpoint_a.get_absolute_url()
        self.assertIn(f'href="{expected_url}"', result)
        self.assertIn("Device A", result)
        self.assertIn("192.168.1.1/24", result)
        self.assertIn("AS 65001", result)

    def test_render_without_ip(self):
        """Test rendering when endpoint A has no IP address."""
        endpoint_without_ip = models.PeerEndpoint.objects.create(
            routing_instance=self.routing_instance_a,
            peering=self.peering_1,
        )
        record = MockRecord(endpoint_a=endpoint_without_ip)
        result = self.column.render(record)
        self.assertIsNone(result)

    def test_render_without_endpoint(self):
        """Test rendering when there's no endpoint A."""
        record = MockRecord(endpoint_a=None)
        result = self.column.render(record)
        self.assertIsNone(result)

    def test_order_ascending(self):
        """Test ordering IP addresses in ascending order."""
        queryset = models.Peering.objects.all()
        ordered_queryset, is_ordered = self.column.order(queryset, False)
        self.assertTrue(is_ordered)

        # Verify the annotations were added
        results = list(ordered_queryset)
        self.assertTrue(hasattr(results[0], "a_endpoint_mask"))
        self.assertTrue(hasattr(results[0], "a_endpoint_ip_version"))
        self.assertTrue(hasattr(results[0], "a_endpoint_host"))

    def test_order_descending(self):
        """Test ordering IP addresses in descending order."""
        queryset = models.Peering.objects.all()
        ordered_queryset, is_ordered = self.column.order(queryset, True)
        self.assertTrue(is_ordered)

        # Verify the annotations were added
        results = list(ordered_queryset)
        self.assertTrue(hasattr(results[0], "a_endpoint_mask"))
        self.assertTrue(hasattr(results[0], "a_endpoint_ip_version"))
        self.assertTrue(hasattr(results[0], "a_endpoint_host"))


class ZEndpointIPColumnTestCase(BaseTableColumnTestCase):
    """Test cases for ZEndpointIPColumn."""

    def setUp(self):
        """Set up test data."""
        self.column = ZEndpointIPColumn()

    def test_render_with_ip(self):
        """Test rendering when endpoint Z has an IP address."""
        record = MockRecord(endpoint_z=self.peer_endpoint_z)
        result = self.column.render(record)

        # hyperlinked_object produces richer output with device and ASN info
        expected_url = reverse("plugins:nautobot_bgp_models:peerendpoint", args=[self.peer_endpoint_z.pk])
        self.assertIn(f'href="{expected_url}"', result)
        self.assertIn("Device Z", result)
        self.assertIn("192.168.1.2/24", result)
        self.assertIn("AS 65002", result)

    def test_render_without_ip(self):
        """Test rendering when endpoint Z has no IP address."""
        endpoint_without_ip = models.PeerEndpoint.objects.create(
            routing_instance=self.routing_instance_z,
            peering=self.peering_1,
        )
        record = MockRecord(endpoint_z=endpoint_without_ip)
        result = self.column.render(record)
        self.assertIsNone(result)

    def test_order_ascending(self):
        """Test ordering IP addresses in ascending order."""
        queryset = models.Peering.objects.all()
        ordered_queryset, is_ordered = self.column.order(queryset, False)
        self.assertTrue(is_ordered)

        # Verify the annotations were added
        results = list(ordered_queryset)
        self.assertTrue(hasattr(results[0], "z_endpoint_mask"))
        self.assertTrue(hasattr(results[0], "z_endpoint_ip_version"))
        self.assertTrue(hasattr(results[0], "z_endpoint_host"))

    def test_order_descending(self):
        """Test ordering IP addresses in descending order."""
        queryset = models.Peering.objects.all()
        ordered_queryset, is_ordered = self.column.order(queryset, True)
        self.assertTrue(is_ordered)

        # Verify the annotations were added
        results = list(ordered_queryset)
        self.assertTrue(hasattr(results[0], "z_endpoint_mask"))
        self.assertTrue(hasattr(results[0], "z_endpoint_ip_version"))
        self.assertTrue(hasattr(results[0], "z_endpoint_host"))


class AASNColumnTestCase(BaseTableColumnTestCase):
    """Test cases for AASNColumn."""

    def setUp(self):
        """Set up test data."""
        self.column = AASNColumn()

    def test_render_with_asn(self):
        """Test rendering when endpoint A has an ASN."""
        record = MockRecord(endpoint_a=self.peer_endpoint_a)
        result = self.column.render(record)

        # hyperlinked_object produces richer output with title and "AS" prefix
        expected_url = reverse("plugins:nautobot_bgp_models:autonomoussystem", args=[self.asn_a.pk])
        self.assertIn(f'href="{expected_url}"', result)
        self.assertIn("AS 65001", result)
        self.assertIn("title=", result)

    def test_render_without_endpoint(self):
        """Test rendering when there's no endpoint A."""
        record = MockRecord(endpoint_a=None)
        result = self.column.render(record)
        self.assertIsNone(result)

    def test_order_ascending(self):
        """Test ordering ASN in ascending order."""
        queryset = models.Peering.objects.all()
        ordered_queryset, is_ordered = self.column.order(queryset, False)
        self.assertTrue(is_ordered)

        # Verify exact sort order (A-side ASNs: 60000, 65001, 65002, 70000)
        results = list(ordered_queryset)
        asn_values = [getattr(result, "a_side_asn_value") for result in results]
        expected_order = [60000, 65001, 65002, 70000]
        self.assertEqual(asn_values, expected_order)

    def test_order_descending(self):
        """Test ordering ASN in descending order."""
        queryset = models.Peering.objects.all()
        ordered_queryset, is_ordered = self.column.order(queryset, True)
        self.assertTrue(is_ordered)

        # Verify exact sort order (A-side ASNs: 70000, 65002, 65001, 60000)
        results = list(ordered_queryset)
        asn_values = [getattr(result, "a_side_asn_value") for result in results]
        expected_order = [70000, 65002, 65001, 60000]
        self.assertEqual(asn_values, expected_order)


class ZASNColumnTestCase(BaseTableColumnTestCase):
    """Test cases for ZASNColumn."""

    def setUp(self):
        """Set up test data."""
        self.column = ZASNColumn()

    def test_render_with_asn(self):
        """Test rendering when endpoint Z has an ASN."""
        record = MockRecord(endpoint_z=self.peer_endpoint_z)
        result = self.column.render(record)

        expected_url = reverse("plugins:nautobot_bgp_models:autonomoussystem", args=[self.asn_z.pk])
        expected_html = f'<a href="{expected_url}">{self.asn_z.asn}</a>'
        self.assertEqual(result, expected_html)

    def test_render_without_endpoint(self):
        """Test rendering when there's no endpoint Z."""
        record = MockRecord(endpoint_z=None)
        result = self.column.render(record)
        self.assertIsNone(result)

    def test_order_ascending(self):
        """Test ordering ASN in ascending order."""
        queryset = models.Peering.objects.all()
        ordered_queryset, is_ordered = self.column.order(queryset, False)
        self.assertTrue(is_ordered)

        # Verify exact sort order (Z-side ASNs: 60000, 65001, 65002, 70000)
        results = list(ordered_queryset)
        asn_values = [getattr(result, "z_side_asn_value") for result in results]
        expected_order = [60000, 65001, 65002, 70000]
        self.assertEqual(asn_values, expected_order)

    def test_order_descending(self):
        """Test ordering ASN in descending order."""
        queryset = models.Peering.objects.all()
        ordered_queryset, is_ordered = self.column.order(queryset, True)
        self.assertTrue(is_ordered)

        # Verify exact sort order (Z-side ASNs: 70000, 65002, 65001, 60000)
        results = list(ordered_queryset)
        asn_values = [getattr(result, "z_side_asn_value") for result in results]
        expected_order = [70000, 65002, 65001, 60000]
        self.assertEqual(asn_values, expected_order)


class AProviderColumnTestCase(BaseTableColumnTestCase):
    """Test cases for AProviderColumn."""

    def setUp(self):
        """Set up test data."""
        self.column = AProviderColumn()

    def test_render_with_provider(self):
        """Test rendering when endpoint A has a provider."""
        record = MockRecord(endpoint_a=self.peer_endpoint_a)
        result = self.column.render(record)

        # hyperlinked_object produces rich output with proper URL and provider name
        expected_url = reverse("circuits:provider", args=[self.provider_a.pk])
        self.assertIn(f'href="{expected_url}"', result)
        self.assertIn("Provider A", result)

    def test_render_without_provider(self):
        """Test rendering when ASN has no provider."""
        # Create ASN without provider
        asn_no_provider = models.AutonomousSystem.objects.create(
            asn=65003, status=self.status_active, description="ASN without provider"
        )
        routing_instance_no_provider = models.BGPRoutingInstance.objects.create(
            device=self.device_a,
            autonomous_system=asn_no_provider,
            status=self.status_active,
        )
        endpoint_no_provider = models.PeerEndpoint.objects.create(
            routing_instance=routing_instance_no_provider,
            peering=self.peering_1,
        )

        record = MockRecord(endpoint_a=endpoint_no_provider)
        result = self.column.render(record)
        self.assertIsNone(result)

    def test_render_without_endpoint(self):
        """Test rendering when there's no endpoint A."""
        record = MockRecord(endpoint_a=None)
        result = self.column.render(record)
        self.assertIsNone(result)

    def test_order_ascending(self):
        """Test ordering provider in ascending order."""
        queryset = models.Peering.objects.all()
        ordered_queryset, is_ordered = self.column.order(queryset, False)
        self.assertTrue(is_ordered)

        # Verify exact sort order (A-side providers: AAA Provider, Provider A, Provider Z, ZZZ Provider)
        results = list(ordered_queryset)
        provider_names = [getattr(result, "a_side_provider_name") for result in results]
        expected_order = ["AAA Provider", "Provider A", "Provider Z", "ZZZ Provider"]
        self.assertEqual(provider_names, expected_order)

    def test_order_descending(self):
        """Test ordering provider in descending order."""
        queryset = models.Peering.objects.all()
        ordered_queryset, is_ordered = self.column.order(queryset, True)
        self.assertTrue(is_ordered)

        # Verify exact sort order (A-side providers: ZZZ Provider, Provider Z, Provider A, AAA Provider)
        results = list(ordered_queryset)
        provider_names = [getattr(result, "a_side_provider_name") for result in results]
        expected_order = ["ZZZ Provider", "Provider Z", "Provider A", "AAA Provider"]
        self.assertEqual(provider_names, expected_order)


class ZProviderColumnTestCase(BaseTableColumnTestCase):
    """Test cases for ZProviderColumn."""

    def setUp(self):
        """Set up test data."""
        self.column = ZProviderColumn()

    def test_render_with_provider(self):
        """Test rendering when endpoint Z has a provider."""
        record = MockRecord(endpoint_z=self.peer_endpoint_z)
        result = self.column.render(record)

        # hyperlinked_object produces rich output with proper URL and provider name
        expected_url = reverse("circuits:provider", args=[self.provider_z.pk])
        self.assertIn(f'href="{expected_url}"', result)
        self.assertIn("Provider Z", result)

    def test_render_without_provider(self):
        """Test rendering when ASN has no provider."""
        # Create ASN without provider
        asn_no_provider = models.AutonomousSystem.objects.create(
            asn=65004, status=self.status_active, description="ASN without provider"
        )
        routing_instance_no_provider = models.BGPRoutingInstance.objects.create(
            device=self.device_z,
            autonomous_system=asn_no_provider,
            status=self.status_active,
        )
        endpoint_no_provider = models.PeerEndpoint.objects.create(
            routing_instance=routing_instance_no_provider,
            peering=self.peering_1,
        )

        record = MockRecord(endpoint_z=endpoint_no_provider)
        result = self.column.render(record)
        self.assertIsNone(result)

    def test_render_without_endpoint(self):
        """Test rendering when there's no endpoint Z."""
        record = MockRecord(endpoint_z=None)
        result = self.column.render(record)
        self.assertIsNone(result)

    def test_order_ascending(self):
        """Test ordering provider in ascending order."""
        queryset = models.Peering.objects.all()
        ordered_queryset, is_ordered = self.column.order(queryset, False)
        self.assertTrue(is_ordered)

        # Verify exact sort order (Z-side providers: AAA Provider, Provider A, Provider Z, ZZZ Provider)
        results = list(ordered_queryset)
        provider_names = [getattr(result, "z_side_provider_name") for result in results]
        expected_order = ["AAA Provider", "Provider A", "Provider Z", "ZZZ Provider"]
        self.assertEqual(provider_names, expected_order)

    def test_order_descending(self):
        """Test ordering provider in descending order."""
        queryset = models.Peering.objects.all()
        ordered_queryset, is_ordered = self.column.order(queryset, True)
        self.assertTrue(is_ordered)

        # Verify exact sort order (Z-side providers: ZZZ Provider, Provider Z, Provider A, AAA Provider)
        results = list(ordered_queryset)
        provider_names = [getattr(result, "z_side_provider_name") for result in results]
        expected_order = ["ZZZ Provider", "Provider Z", "Provider A", "AAA Provider"]
        self.assertEqual(provider_names, expected_order)
