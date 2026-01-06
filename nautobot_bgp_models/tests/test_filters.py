"""Unit test automation for FilterSet classes in nautobot_bgp_models."""

from django.contrib.contenttypes.models import ContentType

# from nautobot.circuits.models import Provider
from nautobot.apps.testing import FilterTestCases
from nautobot.circuits.models import Provider
from nautobot.dcim.choices import InterfaceTypeChoices
from nautobot.dcim.models import Device, DeviceType, Interface, Location, LocationType, Manufacturer
from nautobot.extras.models import Role, Status
from nautobot.ipam.models import VRF, IPAddress, Namespace, Prefix

from nautobot_bgp_models import choices, filters, models


class AutonomousSystemTestCase(FilterTestCases.FilterTestCase):
    """Test filtering of AutonomousSystem records."""

    queryset = models.AutonomousSystem.objects.all()
    filterset = filters.AutonomousSystemFilterSet

    generic_filter_tests = (
        ["asn"],
        ["provider", "provider__id"],
        ["provider", "provider__name"],
        ["status", "status__id"],
        ["status", "status__name"],
    )

    @classmethod
    def setUpTestData(cls):
        """One-time class setup to prepopulate required data for tests."""
        status_active = Status.objects.get(name__iexact="active")
        status_active.content_types.add(ContentType.objects.get_for_model(models.AutonomousSystem))

        cls.status_primary_asn = Status.objects.create(name="Primary ASN", color="FFFFFF")
        cls.status_primary_asn.content_types.add(ContentType.objects.get_for_model(models.AutonomousSystem))

        cls.status_remote_asn = Status.objects.create(name="Remote ASN", color="FFFFFF")
        cls.status_remote_asn.content_types.add(ContentType.objects.get_for_model(models.AutonomousSystem))

        provider_1 = Provider.objects.create(name="Test Provider1")
        provider_2 = Provider.objects.create(name="Test Provider2")
        provider_3 = Provider.objects.create(name="Test Provider3")

        models.AutonomousSystem.objects.create(
            asn=4200000000, status=status_active, provider=provider_1, description="Reserved for private use"
        )
        models.AutonomousSystem.objects.create(
            asn=4200000001,
            status=cls.status_primary_asn,
            provider=provider_2,
            description="Also reserved for private use",
        )
        models.AutonomousSystem.objects.create(
            asn=4200000002,
            status=cls.status_remote_asn,
            provider=provider_3,
            description="Another reserved for private use",
        )

        cls.asn_range = models.AutonomousSystemRange.objects.create(
            name="Private Use ASNs", asn_min=4200000001, asn_max=4294967295, description="Private Use Range"
        )

    def test_search(self):
        """Test filtering by Q search value."""
        self.assertEqual(self.filterset({"q": "420"}, self.queryset).qs.count(), 3)
        self.assertEqual(self.filterset({"q": "another"}, self.queryset).qs.count(), 1)

    def test_asn_range(self):
        """Test filtering by ASN Range."""
        params = {"autonomous_system_range": [self.asn_range.pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class AutonomousSystemRangeTestCase(FilterTestCases.FilterTestCase):
    """Test filtering of AutonomousSystemRange records."""

    queryset = models.AutonomousSystemRange.objects.all()
    filterset = filters.AutonomousSystemRangeFilterSet

    generic_filter_tests = (
        ["name"],
        ["asn_min"],
        ["asn_max"],
    )

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

    def test_search(self):
        """Test filtering by Q search value."""
        self.assertEqual(self.filterset({"q": "DC"}, self.queryset).qs.count(), 2)


class BGPRoutingInstanceTestCase(FilterTestCases.FilterTestCase):
    """Test filtering of BGPRoutingInstance records."""

    queryset = models.BGPRoutingInstance.objects.all()
    filterset = filters.BGPRoutingInstanceFilterSet

    generic_filter_tests = (
        ["autonomous_system", "autonomous_system__asn"],
        ["device", "device__name"],
        ["device", "device__id"],
    )

    @classmethod
    def setUpTestData(cls):  # pylint: disable=too-many-locals
        """One-time class setup to prepopulate required data for tests."""

        status_active = Status.objects.get(name__iexact="active")
        status_active.content_types.add(ContentType.objects.get_for_model(models.AutonomousSystem))
        manufacturer = Manufacturer.objects.create(name="Cisco")
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model="CSR 1000V")
        location_type = LocationType.objects.create(name="site")
        location_status = Status.objects.get_for_model(Location).first()
        location = Location.objects.create(name="Site 1", location_type=location_type, status=location_status)
        devicerole = Role.objects.create(name="Router", color="ff0000")
        devicerole.content_types.add(ContentType.objects.get_for_model(Device))

        asn1 = models.AutonomousSystem.objects.create(asn=65000, status=status_active)
        asn2 = models.AutonomousSystem.objects.create(asn=65001, status=status_active)
        asn3 = models.AutonomousSystem.objects.create(asn=65002, status=status_active)

        device_1 = Device.objects.create(
            device_type=devicetype, role=devicerole, name="Device 1", location=location, status=status_active
        )
        device_2 = Device.objects.create(
            device_type=devicetype, role=devicerole, name="Device 2", location=location, status=status_active
        )
        device_3 = Device.objects.create(
            device_type=devicetype, role=devicerole, name="Device 3", location=location, status=status_active
        )

        namespace = Namespace.objects.first()
        prefix_status = Status.objects.get_for_model(Prefix).first()
        Prefix.objects.create(prefix="1.0.0.0/8", namespace=namespace, status=prefix_status)

        router_id_1 = IPAddress.objects.create(address="1.1.1.1/32", status=status_active, namespace=namespace)
        router_id_2 = IPAddress.objects.create(address="1.1.1.2/32", status=status_active, namespace=namespace)
        router_id_3 = IPAddress.objects.create(address="1.1.1.3/32", status=status_active, namespace=namespace)

        cls.bgp_instance_1 = models.BGPRoutingInstance.objects.create(
            description="BGP routing instance for device 1",
            device=device_1,
            autonomous_system=asn1,
            router_id=router_id_1,
            status=status_active,
        )

        models.BGPRoutingInstance.objects.create(
            description="BGP routing instance for device 2",
            device=device_2,
            autonomous_system=asn2,
            router_id=router_id_2,
            status=status_active,
        )

        models.BGPRoutingInstance.objects.create(
            description="BGP routing instance for device 3",
            device=device_3,
            autonomous_system=asn3,
            router_id=router_id_3,
            status=status_active,
        )

    def test_search(self):
        number_of_devices = models.BGPRoutingInstance.objects.filter(device=self.bgp_instance_1.device).count()
        self.assertEqual(
            self.filterset({"q": self.bgp_instance_1.device.name}, self.queryset).qs.count(), number_of_devices
        )


class PeerGroupTestCase(FilterTestCases.FilterTestCase):
    """Test filtering of PeerGroup records."""

    filterset = filters.PeerGroupFilterSet
    queryset = models.PeerGroup.objects.all()

    generic_filter_tests = (
        ["name"],
        ["autonomous_system", "autonomous_system__asn"],
        ["routing_instance", "routing_instance__id"],
        ["device", "routing_instance__device__name"],
        ["device", "routing_instance__device__id"],
        ["role"],
    )

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
        cls.device_3 = Device.objects.create(
            device_type=devicetype, role=devicerole, name="Device 3", location=location, status=status_active
        )

        cls.asn_1 = models.AutonomousSystem.objects.create(asn=4294967294, status=status_active)
        asn_2 = models.AutonomousSystem.objects.create(asn=4294967295, status=status_active)
        asn_3 = models.AutonomousSystem.objects.create(asn=4294967296, status=status_active)

        cls.peeringrole_internal = Role.objects.create(name="Internal", color="333333")
        cls.peeringrole_internal.content_types.add(ContentType.objects.get_for_model(models.PeerGroup))
        peeringrole_external = Role.objects.create(name="External", color="ffffff")
        peeringrole_external.content_types.add(ContentType.objects.get_for_model(models.PeerGroup))
        peeringrole_transit = Role.objects.create(name="Transit", color="0000ff")
        peeringrole_transit.content_types.add(ContentType.objects.get_for_model(models.PeerGroup))

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
        cls.bgp_routing_instance_3 = models.BGPRoutingInstance.objects.create(
            description="Hello World!",
            autonomous_system=asn_3,
            device=cls.device_3,
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
            routing_instance=cls.bgp_routing_instance_2,
            name="Group C",
            role=cls.peeringrole_internal,
            autonomous_system=asn_2,
            description="Internal Group",
            # vrf=cls.vrf
        )
        models.PeerGroup.objects.create(
            routing_instance=cls.bgp_routing_instance_3,
            name="Group C",
            role=peeringrole_transit,
            autonomous_system=asn_3,
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

    def test_enabled(self):
        """Test filtering by enabled status."""
        params = {"enabled": True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)


class PeerGroupTemplateTestCase(FilterTestCases.FilterTestCase):
    """Test filtering of BGPRoutingInstance records."""

    filterset = filters.PeerGroupTemplateFilterSet
    queryset = models.PeerGroupTemplate.objects.all()

    generic_filter_tests = (
        ["name"],
        ["autonomous_system", "autonomous_system__asn"],
    )

    @classmethod
    def setUpTestData(cls):
        """One-time class setup to prepopulate required data for tests."""

        status_active = Status.objects.get(name__iexact="active")
        status_active.content_types.add(ContentType.objects.get_for_model(models.AutonomousSystem))
        asn1 = models.AutonomousSystem.objects.create(asn=65000, status=status_active)
        asn2 = models.AutonomousSystem.objects.create(asn=65001, status=status_active)
        asn3 = models.AutonomousSystem.objects.create(asn=65002, status=status_active)

        role_internal = Role.objects.create(name="Internal", color="ffffff")
        role_internal.content_types.add(ContentType.objects.get_for_model(models.PeerGroupTemplate))
        role_external = Role.objects.create(name="External", color="ffffff")
        role_external.content_types.add(ContentType.objects.get_for_model(models.PeerGroupTemplate))
        role_transit = Role.objects.create(name="Transit", color="ffffff")
        role_transit.content_types.add(ContentType.objects.get_for_model(models.PeerGroupTemplate))

        cls.peer_group_template_1 = models.PeerGroupTemplate.objects.create(
            name="Template 1",
            role=role_internal,
            description="Hello World",
            autonomous_system=asn1,
        )

        cls.peer_group_template_2 = models.PeerGroupTemplate.objects.create(
            name="Template 2",
            role=role_external,
            description="This is a Peer Group Template",
            autonomous_system=asn2,
        )

        models.PeerGroupTemplate.objects.create(
            name="Template 3",
            role=role_transit,
            description="Hello World",
            enabled=False,
            autonomous_system=asn3,
        )

    def test_enabled(self):
        """Test filtering by enabled status."""
        number_enabled = models.PeerGroupTemplate.objects.filter(enabled=True).count()
        self.assertEqual(self.filterset({"enabled": True}, self.queryset).qs.count(), number_enabled)

    def test_search(self):
        """Test filtering by Q search value."""
        number_of_instances_with_name = models.PeerGroupTemplate.objects.filter(
            name=self.peer_group_template_1.name
        ).count()
        number_of_instances_with_description = models.PeerGroupTemplate.objects.filter(
            description=self.peer_group_template_2.description
        ).count()
        self.assertEqual(
            self.filterset({"q": self.peer_group_template_1.name}, self.queryset).qs.count(),
            number_of_instances_with_name,
        )
        self.assertEqual(
            self.filterset({"q": self.peer_group_template_2.description}, self.queryset).qs.count(),
            number_of_instances_with_description,
        )


class PeerEndpointTestCase(FilterTestCases.FilterTestCase):
    """Test filtering of PeerEndpoint records."""

    queryset = models.PeerEndpoint.objects.all()
    filterset = filters.PeerEndpointFilterSet

    generic_filter_tests = (
        ["device", "routing_instance__device__name"],
        ["device", "routing_instance__device__id"],
        ["autonomous_system", "autonomous_system__asn"],
        ["peer_group", "peer_group__id"],
        ["peer_group", "peer_group__name"],
    )

    @classmethod
    def setUpTestData(cls):  # pylint: disable=too-many-locals
        """One-time class setup."""
        status_active = Status.objects.get(name__iexact="active")
        status_active.content_types.add(ContentType.objects.get_for_model(models.AutonomousSystem))

        asn_1 = models.AutonomousSystem.objects.create(asn=4294967295, status=status_active)
        asn_2 = models.AutonomousSystem.objects.create(asn=4294967296, status=status_active)
        asn_3 = models.AutonomousSystem.objects.create(asn=4294967297, status=status_active)
        peeringrole = Role.objects.create(name="Internal", color="ffffff")
        peeringrole.content_types.add(ContentType.objects.get_for_model(models.PeerGroup))
        manufacturer = Manufacturer.objects.create(name="Cisco")
        cls.devicetype = DeviceType.objects.create(manufacturer=manufacturer, model="CSR 1000V")
        location_type = LocationType.objects.create(name="site")
        location_status = Status.objects.get_for_model(Location).first()
        cls.location = Location.objects.create(name="Site 1", location_type=location_type, status=location_status)
        cls.devicerole = Role.objects.create(name="Router", color="ff0000")
        cls.devicerole.content_types.add(ContentType.objects.get_for_model(Device))
        device_1 = Device.objects.create(
            device_type=cls.devicetype,
            role=cls.devicerole,
            name="Device 1",
            location=cls.location,
            status=status_active,
        )
        device_2 = Device.objects.create(
            device_type=cls.devicetype,
            role=cls.devicerole,
            name="Device 2",
            location=cls.location,
            status=status_active,
        )
        device_3 = Device.objects.create(
            device_type=cls.devicetype,
            role=cls.devicerole,
            name="Device 3",
            location=cls.location,
            status=status_active,
        )
        interface_status = Status.objects.get_for_model(Interface).first()
        interface = Interface.objects.create(
            device=device_1, name="Loopback1", type=InterfaceTypeChoices.TYPE_VIRTUAL, status=interface_status
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

        bgp_routing_instance_1 = models.BGPRoutingInstance.objects.create(
            description="Hello World!",
            autonomous_system=asn_1,
            device=device_1,
            status=status_active,
        )
        bgp_routing_instance_2 = models.BGPRoutingInstance.objects.create(
            description="Hello World!",
            autonomous_system=asn_2,
            device=device_2,
            status=status_active,
        )
        bgp_routing_instance_3 = models.BGPRoutingInstance.objects.create(
            description="Hello World!",
            autonomous_system=asn_3,
            device=device_3,
            status=status_active,
        )

        peergroup_1 = models.PeerGroup.objects.create(
            name="Group B",
            role=peeringrole,
            routing_instance=bgp_routing_instance_1,
        )
        peergroup_2 = models.PeerGroup.objects.create(
            name="Group C",
            role=peeringrole,
            routing_instance=bgp_routing_instance_2,
        )
        peergroup_3 = models.PeerGroup.objects.create(
            name="Group D",
            role=peeringrole,
            routing_instance=bgp_routing_instance_3,
        )

        peering1 = models.Peering.objects.create(status=status_active)
        peering2 = models.Peering.objects.create(status=status_active)
        peering3 = models.Peering.objects.create(status=status_active)

        models.PeerEndpoint.objects.create(
            routing_instance=bgp_routing_instance_1,
            source_ip=addresses[0],
            autonomous_system=asn_1,
            peer_group=peergroup_1,
            peering=peering1,
        )
        models.PeerEndpoint.objects.create(
            routing_instance=bgp_routing_instance_2,
            source_ip=addresses[1],
            autonomous_system=asn_2,
            peer_group=peergroup_2,
            peering=peering2,
        )
        models.PeerEndpoint.objects.create(
            routing_instance=bgp_routing_instance_3,
            source_ip=addresses[2],
            autonomous_system=asn_3,
            peer_group=peergroup_3,
            enabled=False,
            peering=peering3,
        )

    def test_search(self):
        """Test text search."""
        self.assertEqual(self.filterset({"q": "device 1"}, self.queryset).qs.count(), 1)

    def test_enabled(self):
        """Test filtering by enabled status."""
        params = {"enabled": True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class PeeringTestCase(FilterTestCases.FilterTestCase):
    """Test filtering of Peering records."""

    queryset = models.Peering.objects.all()
    filterset = filters.PeeringFilterSet

    generic_filter_tests = (
        ["status", "status__id"],
        ["status", "status__name"],
        ["device", "endpoints__routing_instance__device__name"],
        ["device", "endpoints__routing_instance__device__id"],
        ["device_role", "endpoints__routing_instance__device__role__name"],
        ["peer_endpoint_role", "endpoints__role__name"],
    )

    @classmethod
    def setUpTestData(cls):  # pylint: disable=too-many-statements,too-many-locals
        """One-time class setup to prepopulate required data for tests."""
        status_active = Status.objects.get(name__iexact="active")
        status_active.content_types.add(ContentType.objects.get_for_model(models.Peering))
        status_active.content_types.add(ContentType.objects.get_for_model(models.AutonomousSystem))

        status_reserved = Status.objects.get(name__iexact="reserved")
        status_reserved.content_types.add(ContentType.objects.get_for_model(models.Peering))

        status_planned = Status.objects.get(name__iexact="planned")
        status_planned.content_types.add(ContentType.objects.get_for_model(models.Peering))

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
        devicerole_firewall = Role.objects.create(name="Firewall", color="ff0000")
        device_1 = Device.objects.create(
            device_type=devicetype,
            role=devicerole_router,
            name="device 1",
            location=location,
            status=status_active,
        )
        device_2 = Device.objects.create(
            device_type=devicetype,
            role=devicerole_switch,
            name="device 2",
            location=location,
            status=status_active,
        )
        device_3 = Device.objects.create(
            device_type=devicetype,
            role=devicerole_firewall,
            name="device 3",
            location=location,
            status=status_active,
        )
        device_4 = Device.objects.create(
            device_type=devicetype,
            role=devicerole_firewall,
            name="device 4",
            location=location,
            status=status_active,
        )
        device_5 = Device.objects.create(
            device_type=devicetype,
            role=devicerole_firewall,
            name="device 5",
            location=location,
            status=status_active,
        )
        device_6 = Device.objects.create(
            device_type=devicetype,
            role=devicerole_firewall,
            name="device 6",
            location=location,
            status=status_active,
        )

        bgp_routing_instance_device_1 = models.BGPRoutingInstance.objects.create(
            description="Device 1 RI",
            autonomous_system=asn1,
            device=device_1,
            status=status_active,
        )
        bgp_routing_instance_device_2 = models.BGPRoutingInstance.objects.create(
            description="Device 2 RI",
            autonomous_system=asn1,
            device=device_2,
            status=status_active,
        )
        bgp_routing_instance_device_3 = models.BGPRoutingInstance.objects.create(
            description="Device 3 RI",
            autonomous_system=asn1,
            device=device_3,
            status=status_active,
        )
        bgp_routing_instance_device_4 = models.BGPRoutingInstance.objects.create(
            description="Device 4 RI",
            autonomous_system=asn1,
            device=device_4,
            status=status_active,
        )
        bgp_routing_instance_device_5 = models.BGPRoutingInstance.objects.create(
            description="Device 5 RI",
            autonomous_system=asn1,
            device=device_5,
            status=status_active,
        )
        bgp_routing_instance_device_6 = models.BGPRoutingInstance.objects.create(
            description="Device 6 RI",
            autonomous_system=asn1,
            device=device_6,
            status=status_active,
        )

        interface_status = Status.objects.get_for_model(Interface).first()
        interfaces_device1 = [
            Interface.objects.create(device=device_1, name="Loopback0", status=interface_status),
            Interface.objects.create(device=device_1, name="Loopback1", status=interface_status),
            Interface.objects.create(device=device_1, name="Loopback2", status=interface_status),
        ]
        interfaces_device2 = [
            Interface.objects.create(device=device_2, name="Loopback0", status=interface_status),
            Interface.objects.create(device=device_2, name="Loopback1", status=interface_status),
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

        peeringrole_internal = Role.objects.create(name="Internal", color="ffffff")
        peeringrole_internal.content_types.add(ContentType.objects.get_for_model(models.PeerEndpoint))
        peeringrole_external = Role.objects.create(name="External", color="ffffff")
        peeringrole_external.content_types.add(ContentType.objects.get_for_model(models.PeerEndpoint))
        peeringrole_transit = Role.objects.create(name="Transit", color="ffffff")
        peeringrole_transit.content_types.add(ContentType.objects.get_for_model(models.PeerEndpoint))

        peerings = [
            # Peering #0
            models.Peering.objects.create(status=status_active),
            # Peering #1
            models.Peering.objects.create(status=status_reserved),
            # Peering #2
            models.Peering.objects.create(status=status_planned),
        ]

        # Peering #0
        models.PeerEndpoint.objects.create(
            source_ip=addresses[0],
            peering=peerings[0],
            autonomous_system=asn1,
            role=peeringrole_internal,
            routing_instance=bgp_routing_instance_device_1,
        )
        models.PeerEndpoint.objects.create(
            source_ip=addresses[1],
            peering=peerings[0],
            autonomous_system=asn1,
            routing_instance=bgp_routing_instance_device_4,
        )

        # Peering #1
        models.PeerEndpoint.objects.create(
            source_ip=addresses[2],
            peering=peerings[1],
            autonomous_system=asn1,
            role=peeringrole_external,
            routing_instance=bgp_routing_instance_device_2,
        )
        models.PeerEndpoint.objects.create(
            source_ip=addresses[3],
            peering=peerings[1],
            autonomous_system=asn2,
            routing_instance=bgp_routing_instance_device_5,
        )

        # Peering #2
        models.PeerEndpoint.objects.create(
            source_ip=addresses[4],
            peering=peerings[2],
            autonomous_system=asn1,
            role=peeringrole_transit,
            routing_instance=bgp_routing_instance_device_3,
        )
        models.PeerEndpoint.objects.create(
            source_ip=addresses[5],
            peering=peerings[2],
            autonomous_system=asn3,
            routing_instance=bgp_routing_instance_device_6,
        )

    def test_search(self):
        """Test filtering by Q search value."""
        self.assertEqual(self.filterset({"q": "device 2"}, self.queryset).qs.count(), 1)
        self.assertEqual(self.filterset({"q": "device 3"}, self.queryset).qs.count(), 1)

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


class AddressFamilyTestCase(FilterTestCases.FilterTestCase):
    """Test filtering of AddressFamily records."""

    queryset = models.AddressFamily.objects.all()
    filterset = filters.AddressFamilyFilterSet

    generic_filter_tests = (
        ["vrf"],
        ["afi_safi"],
        ["routing_instance", "routing_instance__id"],
        ["device", "routing_instance__device__name"],
        ["device", "routing_instance__device__id"],
    )

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
        device2 = Device.objects.create(
            device_type=devicetype, role=devicerole, name="Router-8", location=location, status=status_active
        )
        device3 = Device.objects.create(
            device_type=devicetype, role=devicerole, name="Switch-1", location=location, status=status_active
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

        bgp_routing_instance1 = models.BGPRoutingInstance.objects.create(
            description="Hello World!",
            autonomous_system=asn1,
            device=device1,
            status=status_active,
        )
        bgp_routing_instance2 = models.BGPRoutingInstance.objects.create(
            description="Hello World!",
            autonomous_system=asn1,
            device=device2,
            status=status_active,
        )
        bgp_routing_instance3 = models.BGPRoutingInstance.objects.create(
            description="Hello World!",
            autonomous_system=asn1,
            device=device3,
            status=status_active,
        )

        vrf_1 = VRF.objects.create(name="VRF 1", rd="65000:1", status=status_active)
        vrf_2 = VRF.objects.create(name="VRF 2", rd="65000:100", status=status_active)
        vrf_3 = VRF.objects.create(name="VRF 3", rd="65000:200", status=status_active)

        models.AddressFamily.objects.create(
            routing_instance=bgp_routing_instance1,
            afi_safi=choices.AFISAFIChoices.AFI_IPV4_UNICAST,
            vrf=vrf_1,
        )

        models.AddressFamily.objects.create(
            routing_instance=bgp_routing_instance2, afi_safi=choices.AFISAFIChoices.AFI_IPV4_FLOWSPEC, vrf=vrf_2
        )

        models.AddressFamily.objects.create(
            routing_instance=bgp_routing_instance3, afi_safi=choices.AFISAFIChoices.AFI_VPNV4_UNICAST, vrf=vrf_3
        )

    def test_search(self):
        """Test filtering by Q search value."""
        self.assertEqual(self.filterset({"q": "rout"}, self.queryset).qs.count(), 1)


class PeerGroupAddressFamilyTestCase(FilterTestCases.FilterTestCase):
    """Test filtering of PeerGroupAddressFamily records."""

    queryset = models.PeerGroupAddressFamily.objects.all()
    filterset = filters.PeerGroupAddressFamilyFilterSet

    generic_filter_tests = (
        ["afi_safi"],
        ["peer_group", "peer_group__id"],
        ["peer_group", "peer_group__name"],
    )

    @classmethod
    def setUpTestData(cls):  # pylint: disable=too-many-statements
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

        cls.peergroup_1 = models.PeerGroup.objects.create(
            routing_instance=cls.bgp_routing_instance,
            name="Group A",
            role=cls.peeringrole_internal,
            autonomous_system=cls.asn_1,
            description="Internal Group",
        )
        peergroup_2 = models.PeerGroup.objects.create(
            routing_instance=cls.bgp_routing_instance,
            name="Group B",
            role=peeringrole_external,
            autonomous_system=cls.asn_1,
            enabled=False,
            description="External Group",
        )
        peergroup_3 = models.PeerGroup.objects.create(
            routing_instance=cls.bgp_routing_instance,
            name="Group C",
            role=peeringrole_external,
            autonomous_system=cls.asn_1,
            enabled=False,
            description="External Group",
        )

        models.PeerGroupAddressFamily.objects.create(
            peer_group=cls.peergroup_1,
            afi_safi="ipv4_unicast",
        )
        models.PeerGroupAddressFamily.objects.create(
            peer_group=peergroup_2,
            afi_safi="ipv6_unicast",
        )
        models.PeerGroupAddressFamily.objects.create(
            peer_group=peergroup_3,
            afi_safi="ipv4_multicast",
        )

    def test_search(self):
        """Test text search."""
        self.assertEqual(self.filterset({"q": "ipv4"}, self.queryset).qs.count(), 2)
        self.assertEqual(self.filterset({"q": self.peergroup_1.name}, self.queryset).qs.count(), 1)
        self.assertEqual(self.filterset({"q": self.peergroup_1.description}, self.queryset).qs.count(), 1)


class PeerEndpointAddressFamilyTestCase(FilterTestCases.FilterTestCase):
    """Test filtering of PeerEndpointAddressFamily records."""

    queryset = models.PeerEndpointAddressFamily.objects.all()
    filterset = filters.PeerEndpointAddressFamilyFilterSet

    generic_filter_tests = (
        ["afi_safi"],
        ["peer_endpoint", "peer_endpoint__id"],
    )

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
            afi_safi="ipv4_multicast",
        )

    def test_search(self):
        """Test text search."""
        self.assertEqual(self.filterset({"q": "ipv4_uni"}, self.queryset).qs.count(), 2)
        self.assertEqual(self.filterset({"q": "endpoint"}, self.queryset).qs.count(), 2)
        self.assertEqual(self.filterset({"q": "dev"}, self.queryset).qs.count(), 3)
