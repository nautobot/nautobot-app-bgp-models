"""Unit test automation for Model classes in nautobot_bgp_models."""

from django.contrib.contenttypes.models import ContentType
from nautobot.circuits.models import Provider
from nautobot.dcim.models import Device, DeviceRole, DeviceType, Interface, Manufacturer, Site
from nautobot.extras.models import Status
from nautobot.ipam.models import IPAddress
from nautobot.utilities.testing import ViewTestCases

from nautobot_bgp_models import models
from nautobot_bgp_models.choices import AFISAFIChoices
from unittest import skip


class AutonomousSystemTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    """Test views related to the AutonomousSystem model."""

    model = models.AutonomousSystem

    test_bulk_import_objects_without_permission = None
    test_bulk_import_objects_with_permission = None
    test_bulk_import_objects_with_constrained_permission = None

    @skip("Route disabled in commit `c97f037f`")
    def test_bulk_import_objects_with_permission_csv_file(self):
        pass

    @skip("Route disabled in commit `c97f037f`")
    def test_get_object_notes(self):
        pass

    def _get_base_url(self):
        return "plugins:{}:{}_{{}}".format(  # pylint: disable=consider-using-f-string
            self.model._meta.app_label, self.model._meta.model_name
        )

    @classmethod
    def setUpTestData(cls):
        """One-time class data setup."""
        status_active = Status.objects.get(slug="active")
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

        # cls.csv_data = (
        #     "asn,status",
        #     "4200000003,active",
        #     "4200000004,active",
        #     "4200000005,active",
        # )

        cls.bulk_edit_data = {
            "description": "New description",
        }


class PeeringRoleTestCase(ViewTestCases.OrganizationalObjectViewTestCase, ViewTestCases.BulkEditObjectsViewTestCase):
    """Test views related to the PeeringRole model."""

    model = models.PeeringRole

    test_bulk_import_objects_without_permission = None
    test_bulk_import_objects_with_permission = None
    test_bulk_import_objects_with_constrained_permission = None

    @skip("Route disabled in commit `c97f037f`")
    def test_bulk_import_objects_with_permission_csv_file(self):
        pass

    @skip("Route disabled in commit `c97f037f`")
    def test_get_object_notes(self):
        pass

    def _get_base_url(self):
        return "plugins:{}:{}_{{}}".format(  # pylint: disable=consider-using-f-string
            self.model._meta.app_label, self.model._meta.model_name
        )

    @classmethod
    def setUpTestData(cls):
        """One-time class data setup."""
        models.PeeringRole.objects.create(
            name="Internal", slug="internal", color="0000ff", description="Internal peering"
        )
        models.PeeringRole.objects.create(name="Customer", slug="customer", color="ff0000")
        models.PeeringRole.objects.create(name="Tenant", slug="tenant", color="00ff00")

        cls.form_data = {
            "name": "Temporary",
            "slug": "temporary",
            "color": "ffffff",
            "description": "Temporary peering",
        }

        cls.csv_data = (
            "name,slug,color",
            "Role 1,role-1,111111",
            "Role 2,role-2,222222",
            "Role 3,role-3,333333",
        )

        cls.bulk_edit_data = {"color": "123456", "description": "Generic description"}


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

    def _get_base_url(self):
        return "plugins:{}:{}_{{}}".format(  # pylint: disable=consider-using-f-string
            self.model._meta.app_label, self.model._meta.model_name
        )

    @classmethod
    def setUpTestData(cls):
        """One-time class data setup."""

        peeringrole = models.PeeringRole.objects.create(name="Internal", slug="internal", color="ffffff")

        status_active = Status.objects.get(slug="active")
        manufacturer = Manufacturer.objects.create(name="Cisco", slug="cisco")
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model="CSR 1000V", slug="csr1000v")
        site = Site.objects.create(name="Site 1", slug="site-1")
        devicerole = DeviceRole.objects.create(name="Router", slug="router", color="ff0000")
        cls.device_1 = Device.objects.create(
            device_type=devicetype, device_role=devicerole, name="Device 1", site=site, status=status_active
        )

        asn_1 = models.AutonomousSystem.objects.create(asn=4294967294, status=status_active)

        bgp_routing_instance = models.BGPRoutingInstance.objects.create(
            description="Hello World!",
            autonomous_system=asn_1,
            device=cls.device_1,
        )

        models.PeerGroup.objects.create(routing_instance=bgp_routing_instance, name="Group A", role=peeringrole)
        models.PeerGroup.objects.create(routing_instance=bgp_routing_instance, name="Group B", role=peeringrole)
        models.PeerGroup.objects.create(routing_instance=bgp_routing_instance, name="Group C", role=peeringrole)

        cls.form_data = {"name": "Group D", "routing_instance": bgp_routing_instance.pk}

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

    def _get_base_url(self):
        return "plugins:{}:{}_{{}}".format(  # pylint: disable=consider-using-f-string
            self.model._meta.app_label, self.model._meta.model_name
        )

    @classmethod
    def setUpTestData(cls):  # pylint: disable=too-many-locals
        """One-time class data setup."""
        status_active = Status.objects.get(slug="active")

        manufacturer = Manufacturer.objects.create(name="Cisco", slug="cisco")
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model="CSR 1000V", slug="csr1000v")
        site = Site.objects.create(name="Site 1", slug="site-1")
        devicerole = DeviceRole.objects.create(name="Router", slug="router", color="ff0000")
        device = Device.objects.create(
            device_type=devicetype,
            device_role=devicerole,
            name="Device 1",
            site=site,
            status=status_active,
        )
        asn_1 = models.AutonomousSystem.objects.create(asn=4294967294, status=status_active)

        bgp_routing_instance = models.BGPRoutingInstance.objects.create(
            description="Hello World!",
            autonomous_system=asn_1,
            device=device,
        )

        interface = Interface.objects.create(name="Loopback1", device=device)
        interface_2 = Interface.objects.create(name="Loopback2", device=device)
        # vrf = VRF.objects.create(name="red")

        address_1 = IPAddress.objects.create(address="1.1.1.1/32", status=status_active, assigned_object=interface)
        address_3 = IPAddress.objects.create(address="3.3.3.3/32", status=status_active)
        address_2 = IPAddress.objects.create(address="2.2.2.2/32", status=status_active)
        address_4 = IPAddress.objects.create(address="4.4.4.4/32", status=status_active, assigned_object=interface_2)

        peeringrole = models.PeeringRole.objects.create(name="Internal", slug="internal", color="ffffff")

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

    def _get_base_url(self):
        return "plugins:{}:{}_{{}}".format(  # pylint: disable=consider-using-f-string
            self.model._meta.app_label, self.model._meta.model_name
        )

    @classmethod
    def setUpTestData(cls):
        """One-time class data setup."""
        status_active = Status.objects.get(slug="active")
        status_active.content_types.add(ContentType.objects.get_for_model(models.Peering))

        # peeringrole_internal = models.PeeringRole.objects.create(name="Internal", slug="internal", color="000000")
        peeringrole_customer = models.PeeringRole.objects.create(name="Customer", slug="customer", color="ffffff")

        models.Peering.objects.create(status=status_active)
        models.Peering.objects.create(status=status_active)
        models.Peering.objects.create(status=status_active)

        address_1 = IPAddress.objects.create(
            address="1.1.1.1/32",
            status=status_active,
        )

        address_2 = IPAddress.objects.create(
            address="1.1.1.2/32",
            status=status_active,
        )
        provider = Provider.objects.create(name="Provider", slug="provider")

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

    def _get_base_url(self):
        return "plugins:{}:{}_{{}}".format(  # pylint: disable=consider-using-f-string
            self.model._meta.app_label, self.model._meta.model_name
        )

    @classmethod
    def setUpTestData(cls):
        """One-time class data setup."""
        status_active = Status.objects.get(slug="active")

        manufacturer = Manufacturer.objects.create(name="Cisco", slug="cisco")
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model="CSR 1000V", slug="csr1000v")
        site = Site.objects.create(name="Site 1", slug="site-1")
        devicerole = DeviceRole.objects.create(name="Router", slug="router", color="ff0000")
        device = Device.objects.create(
            device_type=devicetype,
            device_role=devicerole,
            name="Device 1",
            site=site,
            status=status_active,
        )
        asn_1 = models.AutonomousSystem.objects.create(asn=4294967294, status=status_active)
        bgp_routing_instance = models.BGPRoutingInstance.objects.create(
            description="Hello World!",
            autonomous_system=asn_1,
            device=device,
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
            "import_policy": "IMPORT",
            "export_policy": "EXPORT",
        }
