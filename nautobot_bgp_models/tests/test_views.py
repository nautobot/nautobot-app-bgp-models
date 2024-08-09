"""Unit test automation for Model classes in nautobot_bgp_models."""

import json
from importlib import metadata
from unittest import skipIf

from django.contrib.contenttypes.models import ContentType
from nautobot.circuits.models import Provider
from nautobot.core.testing import ViewTestCases
from nautobot.dcim.models import Device, DeviceType, Interface, Location, LocationType, Manufacturer
from nautobot.extras.models import Role, Status
from nautobot.ipam.models import IPAddress, Namespace, Prefix
from packaging import version

from nautobot_bgp_models import models
from nautobot_bgp_models.choices import AFISAFIChoices

_NAUTOBOT_VERSION = version.parse(metadata.version("nautobot"))
# Related to this issue: https://github.com/nautobot/nautobot/issues/2948
_FAILING_OBJECT_LIST_NAUTOBOT_VERSIONS = [version.parse("1.5.4"), version.parse("1.5.5")]


class AutonomousSystemTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    """Test views related to the AutonomousSystem model."""

    model = models.AutonomousSystem

    test_bulk_import_objects_without_permission = None
    test_bulk_import_objects_with_permission = None
    test_bulk_import_objects_with_constrained_permission = None

    @skipIf(_NAUTOBOT_VERSION in _FAILING_OBJECT_LIST_NAUTOBOT_VERSIONS, f"Skip Nautobot version {_NAUTOBOT_VERSION}")
    def test_list_objects_with_permission(self):
        super().test_list_objects_with_permission()

    def _get_base_url(self):
        return "plugins:{}:{}_{{}}".format(  # pylint: disable=consider-using-f-string
            self.model._meta.app_label, self.model._meta.model_name
        )

    @classmethod
    def setUpTestData(cls):
        """One-time class data setup."""
        status_active = Status.objects.get(name__iexact="active")
        status_active.content_types.add(ContentType.objects.get_for_model(models.AutonomousSystem))

        models.AutonomousSystem.objects.create(
            asn=4200000000, status=status_active, description="Reserved for private use"
        )
        models.AutonomousSystem.objects.create(
            asn=4200000001, status=status_active, description="Also reserved for private use"
        )
        models.AutonomousSystem.objects.create(
            asn=4200000002, status=status_active, description="Another reserved for private use"
        )

        tags = cls.create_tags("Alpha", "Beta", "Gamma")

        cls.form_data = {
            "asn": 65551,
            "description": "Hello, world!",
            "status": status_active.pk,
            "tags": [tag.pk for tag in tags],
        }

        cls.csv_data = (
            "asn,description,status",
            f"4200000003,asn3,{status_active.name}",
            f"4200000004,asn4,{status_active.name}",
            f"4200000005,asn5,{status_active.name}",
        )

        cls.bulk_edit_data = {
            "description": "New description",
        }


class AutonomousSystemRangeTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    """Test views related to the AutonomousSystemRange model."""

    model = models.AutonomousSystemRange

    @classmethod
    def setUpTestData(cls):
        """One-time class data setup."""
        models.AutonomousSystemRange.objects.create(
            asn_min=1, asn_max=10, name="Private", description="Reserved for private use"
        )
        models.AutonomousSystemRange.objects.create(
            asn_min=11, asn_max=20, name="Private 2", description="Also reserved for private use"
        )
        models.AutonomousSystemRange.objects.create(
            asn_min=21, asn_max=30, name="Private 3", description="Another reserved for private use"
        )

        tags = cls.create_tags("Alpha", "Beta", "Gamma")

        cls.form_data = {
            "name": "Hello World",
            "asn_min": 100,
            "asn_max": 500,
            "description": "Hello, world!",
            "tags": [tag.pk for tag in tags],
        }

        cls.csv_data = (
            "asn_min,asn_max,name,description",
            "1000,2000,range1,range1 descr",
            "2000,4000,range2,range2 descr",
            "5000,9999,range3,range3 descr",
        )

        cls.bulk_edit_data = {
            "description": "New description",
        }


class PeerGroupTestCase(
    ViewTestCases.GetObjectViewTestCase,
    ViewTestCases.GetObjectChangelogViewTestCase,
    ViewTestCases.CreateObjectViewTestCase,
    ViewTestCases.EditObjectViewTestCase,
    ViewTestCases.DeleteObjectViewTestCase,
    ViewTestCases.ListObjectsViewTestCase,
):
    """Test views related to the PeerGroup model."""

    model = models.PeerGroup

    test_create_object_with_constrained_permission = None  # TODO(mzb): FIXME

    @skipIf(_NAUTOBOT_VERSION in _FAILING_OBJECT_LIST_NAUTOBOT_VERSIONS, f"Skip Nautobot version {_NAUTOBOT_VERSION}")
    def test_list_objects_with_permission(self):
        super().test_list_objects_with_permission()

    def _get_base_url(self):
        return "plugins:{}:{}_{{}}".format(  # pylint: disable=consider-using-f-string
            self.model._meta.app_label, self.model._meta.model_name
        )

    @classmethod
    def setUpTestData(cls):
        """One-time class data setup."""

        peeringrole = Role.objects.create(name="Internal", color="ffffff")
        peeringrole.content_types.add(ContentType.objects.get_for_model(models.PeerGroup))

        status_active = Status.objects.get(name__iexact="active")
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

        asn_1 = models.AutonomousSystem.objects.create(asn=4294967294, status=status_active)

        bgp_routing_instance = models.BGPRoutingInstance.objects.create(
            description="Hello World!",
            autonomous_system=asn_1,
            device=cls.device_1,
            status=status_active,
        )

        models.PeerGroup.objects.create(routing_instance=bgp_routing_instance, name="Group A", role=peeringrole)
        models.PeerGroup.objects.create(routing_instance=bgp_routing_instance, name="Group B", role=peeringrole)
        models.PeerGroup.objects.create(routing_instance=bgp_routing_instance, name="Group C", role=peeringrole)

        cls.form_data = {"name": "Group D", "routing_instance": bgp_routing_instance.pk}

        cls.csv_data = (
            "name,routing_instance",
            f"Group E,{bgp_routing_instance.pk}",
            f"Group F,{bgp_routing_instance.pk}",
            f"Group G,{bgp_routing_instance.pk}",
        )

        cls.bulk_edit_data = {"description": "Generic description"}


class PeerEndpointTestCase(
    ViewTestCases.GetObjectViewTestCase,
    ViewTestCases.GetObjectChangelogViewTestCase,
    # TODO Investigate how to enable tests that requires additional parameters (peering)
    # ViewTestCases.CreateObjectViewTestCase,
    # ViewTestCases.EditObjectViewTestCase,
    ViewTestCases.DeleteObjectViewTestCase,
    ViewTestCases.ListObjectsViewTestCase,
):
    """Test views related to the PeerEndpoint model."""

    model = models.PeerEndpoint
    maxDiff = None

    @skipIf(_NAUTOBOT_VERSION in _FAILING_OBJECT_LIST_NAUTOBOT_VERSIONS, f"Skip Nautobot version {_NAUTOBOT_VERSION}")
    def test_list_objects_with_permission(self):
        super().test_list_objects_with_permission()

    def _get_base_url(self):
        return "plugins:{}:{}_{{}}".format(  # pylint: disable=consider-using-f-string
            self.model._meta.app_label, self.model._meta.model_name
        )

    @classmethod
    def setUpTestData(cls):  # pylint: disable=too-many-locals
        """One-time class data setup."""
        status_active = Status.objects.get(name__iexact="active")

        manufacturer = Manufacturer.objects.create(name="Cisco")
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model="CSR 1000V")
        location_type = LocationType.objects.create(name="site")
        location_status = Status.objects.get_for_model(Location).first()
        location = Location.objects.create(name="Site 1", location_type=location_type, status=location_status)
        devicerole = Role.objects.create(name="Router", color="ff0000")
        devicerole.content_types.add(ContentType.objects.get_for_model(Device))
        device = Device.objects.create(
            device_type=devicetype,
            role=devicerole,
            name="Device 1",
            location=location,
            status=status_active,
        )
        asn_1 = models.AutonomousSystem.objects.create(asn=4294967294, status=status_active)

        bgp_routing_instance = models.BGPRoutingInstance.objects.create(
            description="Hello World!",
            autonomous_system=asn_1,
            device=device,
            status=status_active,
        )
        interface_status = Status.objects.get_for_model(Interface).first()
        interface = Interface.objects.create(name="Loopback1", device=device, status=interface_status)
        interface_2 = Interface.objects.create(name="Loopback2", device=device, status=interface_status)
        # vrf = VRF.objects.create(name="red")

        namespace = Namespace.objects.first()
        prefix_status = Status.objects.get_for_model(Prefix).first()
        Prefix.objects.create(prefix="1.0.0.0/8", namespace=namespace, status=prefix_status)
        Prefix.objects.create(prefix="2.0.0.0/8", namespace=namespace, status=prefix_status)
        Prefix.objects.create(prefix="3.0.0.0/8", namespace=namespace, status=prefix_status)
        Prefix.objects.create(prefix="4.0.0.0/8", namespace=namespace, status=prefix_status)

        address_1 = IPAddress.objects.create(address="1.1.1.1/32", status=status_active, namespace=namespace)
        address_3 = IPAddress.objects.create(address="3.3.3.3/32", status=status_active, namespace=namespace)
        address_2 = IPAddress.objects.create(address="2.2.2.2/32", status=status_active, namespace=namespace)
        address_4 = IPAddress.objects.create(address="4.4.4.4/32", status=status_active, namespace=namespace)

        interface.add_ip_addresses(address_1)
        interface_2.add_ip_addresses(address_4)

        peeringrole = Role.objects.create(name="Internal", color="ffffff")
        peeringrole.content_types.add(ContentType.objects.get_for_model(models.PeerGroup))

        peergroup = models.PeerGroup.objects.create(
            name="Group A",
            role=peeringrole,
            routing_instance=bgp_routing_instance,
        )

        peering1 = models.Peering.objects.create(
            status=status_active,
        )
        peering2 = models.Peering.objects.create(
            status=status_active,
        )
        peering3 = models.Peering.objects.create(
            status=status_active,
        )

        models.PeerEndpoint.objects.create(
            source_ip=address_1,
            peer_group=peergroup,
            peering=peering1,
            routing_instance=bgp_routing_instance,
        )

        models.PeerEndpoint.objects.create(source_ip=address_2, peering=peering2, routing_instance=bgp_routing_instance)
        models.PeerEndpoint.objects.create(source_ip=address_3, peering=peering3, routing_instance=bgp_routing_instance)

        cls.form_data = {
            "source_ip": address_4.pk,
            "peer_group": peergroup.pk,
            "peering": peering2.pk,
        }


class PeeringTestCase(
    ViewTestCases.GetObjectViewTestCase,
    ViewTestCases.GetObjectChangelogViewTestCase,
    # TODO Investigate how to enable tests that requires additional parameters (peering)
    # ViewTestCases.CreateObjectViewTestCase,
    ViewTestCases.EditObjectViewTestCase,
    ViewTestCases.DeleteObjectViewTestCase,
    ViewTestCases.ListObjectsViewTestCase,
):
    """Test views related to the Peering model."""

    model = models.Peering
    maxDiff = None

    @skipIf(_NAUTOBOT_VERSION in _FAILING_OBJECT_LIST_NAUTOBOT_VERSIONS, f"Skip Nautobot version {_NAUTOBOT_VERSION}")
    def test_list_objects_with_permission(self):
        super().test_list_objects_with_permission()

    def _get_base_url(self):
        return "plugins:{}:{}_{{}}".format(  # pylint: disable=consider-using-f-string
            self.model._meta.app_label, self.model._meta.model_name
        )

    @classmethod
    def setUpTestData(cls):
        """One-time class data setup."""
        status_active = Status.objects.get(name__iexact="active")
        status_active.content_types.add(ContentType.objects.get_for_model(models.Peering))

        # peeringrole_internal = models.PeeringRole.objects.create(name="Internal", slug="internal", color="000000")
        peeringrole_customer = Role.objects.create(name="Customer", color="ffffff")
        peeringrole_customer.content_types.add(ContentType.objects.get_for_model(models.Peering))

        models.Peering.objects.create(status=status_active)
        models.Peering.objects.create(status=status_active)
        models.Peering.objects.create(status=status_active)

        namespace = Namespace.objects.first()
        prefix_status = Status.objects.get_for_model(Prefix).first()
        Prefix.objects.create(prefix="1.0.0.0/8", namespace=namespace, status=prefix_status)

        address_1 = IPAddress.objects.create(
            address="1.1.1.1/32",
            status=status_active,
            namespace=namespace,
        )

        address_2 = IPAddress.objects.create(
            address="1.1.1.2/32",
            status=status_active,
            namespace=namespace,
        )
        provider = Provider.objects.create(name="Provider")

        asn_1 = models.AutonomousSystem.objects.create(asn=4294967290, status=status_active, provider=provider)
        asn_2 = models.AutonomousSystem.objects.create(asn=4294967291, status=status_active, provider=provider)

        cls.form_data = {
            "status": status_active.pk,
            "role": peeringrole_customer.pk,
            "peerendpoint_a_autonomous_system": asn_1.pk,
            "peerendpoint_z_autonomous_system": asn_2.pk,
            "peerendpoint_a_source_ip": address_1.pk,
            "peerendpoint_z_source_ip": address_2.pk,
        }


class AddressFamilyTestCase(
    ViewTestCases.GetObjectViewTestCase,
    ViewTestCases.GetObjectChangelogViewTestCase,
    ViewTestCases.CreateObjectViewTestCase,
    ViewTestCases.EditObjectViewTestCase,
    ViewTestCases.DeleteObjectViewTestCase,
    ViewTestCases.ListObjectsViewTestCase,
):
    """Test views related to the AddressFamily model."""

    model = models.AddressFamily
    maxDiff = None

    test_create_object_with_constrained_permission = None  # TODO(mzb): FIXME

    @skipIf(_NAUTOBOT_VERSION in _FAILING_OBJECT_LIST_NAUTOBOT_VERSIONS, f"Skip Nautobot version {_NAUTOBOT_VERSION}")
    def test_list_objects_with_permission(self):
        super().test_list_objects_with_permission()

    def _get_base_url(self):
        return "plugins:{}:{}_{{}}".format(  # pylint: disable=consider-using-f-string
            self.model._meta.app_label, self.model._meta.model_name
        )

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
        device = Device.objects.create(
            device_type=devicetype,
            role=devicerole,
            name="Device 1",
            location=location,
            status=status_active,
        )
        asn_1 = models.AutonomousSystem.objects.create(asn=4294967294, status=status_active)
        bgp_routing_instance = models.BGPRoutingInstance.objects.create(
            description="Hello World!",
            autonomous_system=asn_1,
            device=device,
            status=status_active,
        )

        models.AddressFamily.objects.create(
            routing_instance=bgp_routing_instance, afi_safi=AFISAFIChoices.AFI_IPV4_UNICAST
        )
        models.AddressFamily.objects.create(
            routing_instance=bgp_routing_instance, afi_safi=AFISAFIChoices.AFI_IPV4_MULTICAST
        )
        models.AddressFamily.objects.create(
            routing_instance=bgp_routing_instance, afi_safi=AFISAFIChoices.AFI_IPV4_FLOWSPEC
        )

        cls.form_data = {
            "routing_instance": bgp_routing_instance.pk,
            "afi_safi": AFISAFIChoices.AFI_IPV6_UNICAST,
        }


class PeerGroupAddressFamilyTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    """Test views related to the PeerGroupAddressFamily model."""

    model = models.PeerGroupAddressFamily

    def _get_base_url(self):
        return "plugins:{}:{}_{{}}".format(  # pylint: disable=consider-using-f-string
            self.model._meta.app_label, self.model._meta.model_name
        )

    @classmethod
    def setUpTestData(cls):
        """One-time class data setup."""
        peeringrole = Role.objects.create(name="Internal", color="ffffff")
        peeringrole.content_types.add(ContentType.objects.get_for_model(models.PeerGroup))

        status_active = Status.objects.get(name__iexact="active")
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

        asn_1 = models.AutonomousSystem.objects.create(asn=4294967294, status=status_active)

        bgp_routing_instance = models.BGPRoutingInstance.objects.create(
            description="Hello World!",
            autonomous_system=asn_1,
            device=cls.device_1,
            status=status_active,
        )

        pg1 = models.PeerGroup.objects.create(routing_instance=bgp_routing_instance, name="Group A", role=peeringrole)
        pg2 = models.PeerGroup.objects.create(routing_instance=bgp_routing_instance, name="Group B", role=peeringrole)

        models.PeerGroupAddressFamily.objects.create(
            peer_group=pg1,
            afi_safi="ipv4_unicast",
            import_policy="IMPORT",
            export_policy="EXPORT",
            multipath=True,
            extra_attributes={"key": "value"},
        )
        models.PeerGroupAddressFamily.objects.create(
            peer_group=pg1,
            afi_safi="ipv6_unicast",
        )
        models.PeerGroupAddressFamily.objects.create(
            peer_group=pg2,
            afi_safi="ipv4_unicast",
        )

        cls.form_data = {
            "afi_safi": "vpnv4_unicast",
            "peer_group": pg1.pk,
            "import_policy": "IMPORT V2",
            "export_policy": "EXPORT V2",
            "multipath": False,
            "extra_attributes": json.dumps({"key": "value"}),
        }

        cls.csv_data = (
            "afi_safi,peer_group,import_policy,export_policy",
            f"ipv6_unicast,{pg2.pk},IMPORT,EXPORT",
            f"vpnv4_unicast,{pg2.pk},,",
            f"l2_evpn,{pg1.pk},,",
        )

        cls.bulk_edit_data = {"import_policy": "IMPORT V2", "export_policy": "EXPORT V2", "multipath": False}

    @skipIf(_NAUTOBOT_VERSION in _FAILING_OBJECT_LIST_NAUTOBOT_VERSIONS, f"Skip Nautobot version {_NAUTOBOT_VERSION}")
    def test_list_objects_with_permission(self):
        super().test_list_objects_with_permission()


class PeerEndpointAddressFamilyTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    """Test views related to the PeerEndpointAddressFamily model."""

    model = models.PeerEndpointAddressFamily
    maxDiff = None

    @skipIf(_NAUTOBOT_VERSION in _FAILING_OBJECT_LIST_NAUTOBOT_VERSIONS, f"Skip Nautobot version {_NAUTOBOT_VERSION}")
    def test_list_objects_with_permission(self):
        super().test_list_objects_with_permission()

    def _get_base_url(self):
        return "plugins:{}:{}_{{}}".format(  # pylint: disable=consider-using-f-string
            self.model._meta.app_label, self.model._meta.model_name
        )

    @classmethod
    def setUpTestData(cls):  # pylint: disable=too-many-locals
        """One-time class data setup."""
        status_active = Status.objects.get(name__iexact="active")

        manufacturer = Manufacturer.objects.create(name="Cisco")
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model="CSR 1000V")
        location_type = LocationType.objects.create(name="site")
        location_status = Status.objects.get_for_model(Location).first()
        location = Location.objects.create(name="Site 1", location_type=location_type, status=location_status)
        devicerole = Role.objects.create(name="Router", color="ff0000")
        devicerole.content_types.add(ContentType.objects.get_for_model(Device))

        device = Device.objects.create(
            device_type=devicetype,
            role=devicerole,
            name="Device 1",
            location=location,
            status=status_active,
        )
        asn_1 = models.AutonomousSystem.objects.create(asn=4294967294, status=status_active)

        bgp_routing_instance = models.BGPRoutingInstance.objects.create(
            description="Hello World!",
            autonomous_system=asn_1,
            device=device,
            status=status_active,
        )

        # vrf = VRF.objects.create(name="red")
        cls.namespace = Namespace.objects.first()
        prefix_status = Status.objects.get_for_model(Prefix).first()
        Prefix.objects.create(prefix="1.0.0.0/8", namespace=cls.namespace, status=prefix_status)
        Prefix.objects.create(prefix="2.0.0.0/8", namespace=cls.namespace, status=prefix_status)

        address_1 = IPAddress.objects.create(address="1.1.1.1/32", status=status_active, namespace=cls.namespace)
        address_2 = IPAddress.objects.create(address="2.2.2.2/32", status=status_active, namespace=cls.namespace)

        interface = Interface.objects.create(name="Loopback1", device=device, status=status_active)
        interface.add_ip_addresses(address_1)

        peeringrole = Role.objects.create(name="Internal", color="ffffff")
        peeringrole.content_types.add(ContentType.objects.get_for_model(models.PeerGroup))

        peergroup = models.PeerGroup.objects.create(
            name="Group A",
            role=peeringrole,
            routing_instance=bgp_routing_instance,
        )

        peering1 = models.Peering.objects.create(
            status=status_active,
        )
        peering2 = models.Peering.objects.create(
            status=status_active,
        )

        pe1 = models.PeerEndpoint.objects.create(
            source_ip=address_1,
            peer_group=peergroup,
            peering=peering1,
            routing_instance=bgp_routing_instance,
        )
        pe2 = models.PeerEndpoint.objects.create(
            source_ip=address_2,
            peering=peering2,
            routing_instance=bgp_routing_instance,
        )

        models.PeerEndpointAddressFamily.objects.create(
            peer_endpoint=pe1, afi_safi="ipv4_unicast", import_policy="IMPORT", export_policy="EXPORT", multipath=True
        )
        models.PeerEndpointAddressFamily.objects.create(peer_endpoint=pe1, afi_safi="ipv6_unicast")
        models.PeerEndpointAddressFamily.objects.create(peer_endpoint=pe2, afi_safi="ipv4_unicast")

        cls.form_data = {
            "peer_endpoint": pe1.pk,
            "afi_safi": "vpnv4_unicast",
            "import_policy": "IMPORTv2",
            "export_policy": "EXPORTv2",
            "multipath": False,
            "extra_attributes": json.dumps({"key": "value"}),
        }

        cls.csv_data = [
            "peer_endpoint,afi_safi,import_policy,export_policy",
            f"{pe1.pk},vpnv4_unicast,IMPORTv2,EXPORTv2",
            f"{pe2.pk},vpnv4_unicast,,",
        ]

        cls.bulk_edit_data = {"import_policy": "foo", "export_policy": "bar"}
