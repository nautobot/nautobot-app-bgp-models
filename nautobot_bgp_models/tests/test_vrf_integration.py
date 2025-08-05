"""Unit tests for VRF integration in BGP models."""

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.test import TestCase
from nautobot.dcim.models import Device, DeviceType, Location, LocationType, Manufacturer
from nautobot.extras.models import Role, Status
from nautobot.ipam.models import VRF, Namespace, Prefix

from nautobot_bgp_models import filters, forms, models
from nautobot_bgp_models.choices import AFISAFIChoices


class VRFIntegrationTestCase(TestCase):
    """Test the VRF integration across BGP models."""

    @classmethod
    def setUpTestData(cls):
        """One-time class data setup."""
        cls.status_active = Status.objects.get(name__iexact="active")
        cls.status_active.content_types.add(ContentType.objects.get_for_model(models.AutonomousSystem))
        cls.status_active.content_types.add(ContentType.objects.get_for_model(models.BGPRoutingInstance))
        cls.status_active.content_types.add(ContentType.objects.get_for_model(models.Peering))

        # Create base objects
        manufacturer = Manufacturer.objects.create(name="Cisco")
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model="CSR 1000V")
        location_type = LocationType.objects.create(name="site")
        location_status = Status.objects.get_for_model(Location).first()
        location = Location.objects.create(name="Site 1", location_type=location_type, status=location_status)
        devicerole = Role.objects.create(name="Router", color="ff0000")
        devicerole.content_types.add(ContentType.objects.get_for_model(Device))

        # Create devices
        cls.device_1 = Device.objects.create(
            device_type=devicetype,
            role=devicerole,
            name="Device 1",
            location=location,
            status=cls.status_active,
        )
        cls.device_2 = Device.objects.create(
            device_type=devicetype,
            role=devicerole,
            name="Device 2",
            location=location,
            status=cls.status_active,
        )

        # Create VRFs
        cls.vrf_red = VRF.objects.create(name="red")
        cls.vrf_blue = VRF.objects.create(name="blue")

        # Create AS
        cls.autonomous_system = models.AutonomousSystem.objects.create(
            asn=65000, status=cls.status_active, description="Test AS"
        )

        # Create namespace for IP addresses
        cls.namespace = Namespace.objects.first()
        prefix_status = Status.objects.get_for_model(Prefix).first()
        Prefix.objects.create(prefix="10.0.0.0/8", namespace=cls.namespace, status=prefix_status)

        # Create BGP instances with different VRFs for filter tests
        cls.bgp_instance_red = models.BGPRoutingInstance.objects.create(
            description="BGP Instance with red VRF",
            autonomous_system=cls.autonomous_system,
            device=cls.device_1,
            vrf=cls.vrf_red,
            status=cls.status_active,
        )

        cls.bgp_instance_blue = models.BGPRoutingInstance.objects.create(
            description="BGP Instance with blue VRF",
            autonomous_system=cls.autonomous_system,
            device=cls.device_1,
            vrf=cls.vrf_blue,
            status=cls.status_active,
        )

        cls.bgp_instance_no_vrf = models.BGPRoutingInstance.objects.create(
            description="BGP Instance without VRF",
            autonomous_system=cls.autonomous_system,
            device=cls.device_2,
            status=cls.status_active,
        )

        # Create Peer Groups
        cls.peer_group_red = models.PeerGroup.objects.create(
            name="PG Red",
            routing_instance=cls.bgp_instance_red,
            vrf=cls.vrf_red,
        )

        cls.peer_group_blue = models.PeerGroup.objects.create(
            name="PG Blue",
            routing_instance=cls.bgp_instance_blue,
            vrf=cls.vrf_blue,
        )

        cls.peer_group_no_vrf = models.PeerGroup.objects.create(
            name="PG No VRF",
            routing_instance=cls.bgp_instance_no_vrf,
        )

        # Create Address Families
        cls.address_family_red = models.AddressFamily.objects.create(
            routing_instance=cls.bgp_instance_red,
            afi_safi=AFISAFIChoices.AFI_IPV4_UNICAST,
            vrf=cls.vrf_red,
        )

        cls.address_family_blue = models.AddressFamily.objects.create(
            routing_instance=cls.bgp_instance_blue,
            afi_safi=AFISAFIChoices.AFI_IPV4_UNICAST,
            vrf=cls.vrf_blue,
        )

        cls.address_family_no_vrf = models.AddressFamily.objects.create(
            routing_instance=cls.bgp_instance_no_vrf,
            afi_safi=AFISAFIChoices.AFI_IPV4_UNICAST,
        )

    def test_bgp_routing_instance_with_vrf(self):
        """Test BGPRoutingInstance with VRF."""
        # Create a new autonomous system for this test to avoid uniqueness constraint violations
        test_autonomous_system = models.AutonomousSystem.objects.create(
            asn=65001, status=self.status_active, description="Test AS for VRF test"
        )

        # Create a BGPRoutingInstance with VRF - use device_2 to avoid uniqueness constraint with existing instances
        bgp_instance_with_vrf = models.BGPRoutingInstance.objects.create(
            description="BGP Instance with VRF",
            autonomous_system=test_autonomous_system,
            device=self.device_2,  # Use device_2 instead of device_1
            vrf=self.vrf_red,
            status=self.status_active,
        )

        # Verify the instance was created correctly
        self.assertEqual(bgp_instance_with_vrf.vrf, self.vrf_red)

        # Verify string representation includes VRF
        self.assertEqual(str(bgp_instance_with_vrf), f"{self.device_2} - {test_autonomous_system} (VRF {self.vrf_red})")

        # Test creating a second instance with same device, AS, but different VRF
        bgp_instance_with_different_vrf = models.BGPRoutingInstance.objects.create(
            description="BGP Instance with different VRF",
            autonomous_system=test_autonomous_system,
            device=self.device_2,
            vrf=self.vrf_blue,
            status=self.status_active,
        )

        self.assertEqual(bgp_instance_with_different_vrf.vrf, self.vrf_blue)

        # Test uniqueness constraint - creating another instance with same device, AS, and VRF should fail
        with self.assertRaises(ValidationError):
            models.BGPRoutingInstance(
                description="Duplicate BGP Instance",
                autonomous_system=test_autonomous_system,
                device=self.device_2,
                vrf=self.vrf_red,
                status=self.status_active,
            ).validated_save()

    def test_peer_group_with_vrf(self):
        """Test PeerGroup with VRF."""
        # Create a new AS for this test
        test_autonomous_system = models.AutonomousSystem.objects.create(
            asn=65002, status=self.status_active, description="Test AS for PeerGroup VRF test"
        )

        # Create a BGPRoutingInstance without VRF for this test
        test_bgp_instance = models.BGPRoutingInstance.objects.create(
            description="BGP Instance for PeerGroup VRF test",
            autonomous_system=test_autonomous_system,
            device=self.device_2,
            status=self.status_active,
        )

        # Create a PeerGroup with VRF
        peer_group_with_vrf = models.PeerGroup.objects.create(
            name="Test Peer Group with VRF",  # Use a unique name
            routing_instance=test_bgp_instance,
            vrf=self.vrf_red,
        )

        # Verify the PeerGroup was created correctly
        self.assertEqual(peer_group_with_vrf.vrf, self.vrf_red)

        # Test uniqueness constraint - creating another PeerGroup with same name, routing instance, and VRF should fail
        with self.assertRaises(ValidationError):
            models.PeerGroup(
                name="Test Peer Group with VRF",
                routing_instance=test_bgp_instance,
                vrf=self.vrf_red,
            ).validated_save()

        # Test creating a PeerGroup with same name, routing instance, but different VRF
        peer_group_with_different_vrf = models.PeerGroup.objects.create(
            name="Test Peer Group with VRF",
            routing_instance=test_bgp_instance,
            vrf=self.vrf_blue,
        )

        self.assertEqual(peer_group_with_different_vrf.vrf, self.vrf_blue)

        # Test creating a PeerGroup with same name, routing instance, and no VRF
        peer_group_without_vrf = models.PeerGroup.objects.create(
            name="Test Peer Group with VRF",
            routing_instance=test_bgp_instance,
            vrf=None,
        )

        self.assertIsNone(peer_group_without_vrf.vrf)

    def test_address_family_with_vrf(self):
        """Test AddressFamily with VRF."""
        # Create a new AS for this test
        test_autonomous_system = models.AutonomousSystem.objects.create(
            asn=65003, status=self.status_active, description="Test AS for AddressFamily VRF test"
        )

        # Create a BGPRoutingInstance
        test_bgp_instance = models.BGPRoutingInstance.objects.create(
            description="BGP Instance for AddressFamily VRF test",
            autonomous_system=test_autonomous_system,
            device=self.device_2,
            status=self.status_active,
        )

        # Create an AddressFamily with VRF
        address_family_with_vrf = models.AddressFamily.objects.create(
            routing_instance=test_bgp_instance,
            afi_safi=AFISAFIChoices.AFI_IPV4_UNICAST,
            vrf=self.vrf_red,
        )

        # Verify the AddressFamily was created correctly
        self.assertEqual(address_family_with_vrf.vrf, self.vrf_red)

        # Verify string representation includes VRF
        self.assertEqual(
            str(address_family_with_vrf), f"{AFISAFIChoices.AFI_IPV4_UNICAST} AF (VRF {self.vrf_red}) {self.device_2}"
        )

        # Test uniqueness validation - creating another AddressFamily with same routing instance, AFI-SAFI, and VRF should fail
        with self.assertRaises(ValidationError):
            address_family_duplicate = models.AddressFamily(
                routing_instance=test_bgp_instance,
                afi_safi=AFISAFIChoices.AFI_IPV4_UNICAST,
                vrf=self.vrf_red,
            )
            # Need to explicitly call validate_unique to trigger the uniqueness check
            address_family_duplicate.validate_unique()

        # Test creating an AddressFamily with same routing instance, AFI-SAFI, but different VRF
        address_family_with_different_vrf = models.AddressFamily.objects.create(
            routing_instance=test_bgp_instance,
            afi_safi=AFISAFIChoices.AFI_IPV4_UNICAST,
            vrf=self.vrf_blue,
        )

        self.assertEqual(address_family_with_different_vrf.vrf, self.vrf_blue)

        # Test creating an AddressFamily with same routing instance, AFI-SAFI, and no VRF
        address_family_without_vrf = models.AddressFamily.objects.create(
            routing_instance=test_bgp_instance,
            afi_safi=AFISAFIChoices.AFI_IPV6_UNICAST,  # Different AFI-SAFI
            vrf=None,
        )

        self.assertIsNone(address_family_without_vrf.vrf)

        # Verify string representation without VRF
        self.assertEqual(str(address_family_without_vrf), f"{AFISAFIChoices.AFI_IPV6_UNICAST} AF - {self.device_2}")

        # Test uniqueness validation - creating another AddressFamily with same routing instance, AFI-SAFI and no VRF should fail
        with self.assertRaises(ValidationError):
            address_family_duplicate = models.AddressFamily(
                routing_instance=test_bgp_instance,
                afi_safi=AFISAFIChoices.AFI_IPV6_UNICAST,
                vrf=None,
            )
            # Need to explicitly call validate_unique to trigger the uniqueness check
            address_family_duplicate.validate_unique()

    def test_peer_group_address_family_with_vrf(self):
        """Test PeerGroupAddressFamily with inherited VRF."""
        # Create a new AS for this test
        test_autonomous_system = models.AutonomousSystem.objects.create(
            asn=65004, status=self.status_active, description="Test AS for PeerGroupAddressFamily VRF test"
        )

        # Create a BGPRoutingInstance
        test_bgp_instance = models.BGPRoutingInstance.objects.create(
            description="BGP Instance for PeerGroupAddressFamily VRF test",
            autonomous_system=test_autonomous_system,
            device=self.device_2,
            status=self.status_active,
        )

        # Create a PeerGroup with VRF
        peer_group = models.PeerGroup.objects.create(
            name="Test PeerGroup for AddressFamily",
            routing_instance=test_bgp_instance,
            vrf=self.vrf_red,
        )

        # Create an AddressFamily for the same routing instance and VRF
        address_family = models.AddressFamily.objects.create(
            routing_instance=test_bgp_instance,
            afi_safi=AFISAFIChoices.AFI_IPV4_UNICAST,
            vrf=self.vrf_red,
        )

        # Create a PeerGroupAddressFamily
        peer_group_af = models.PeerGroupAddressFamily.objects.create(
            peer_group=peer_group,
            afi_safi=AFISAFIChoices.AFI_IPV4_UNICAST,
        )

        # Test that PeerGroupAddressFamily correctly inherits from the AddressFamily
        self.assertEqual(peer_group_af.parent_address_family, address_family)

        # Verify PeerGroupAddressFamily has access to the VRF through its relationships
        self.assertEqual(peer_group_af.peer_group.vrf, self.vrf_red)

    def test_bgp_routing_instance_filter_form_vrf_field(self):
        """Test VRF field in BGPRoutingInstanceFilterForm."""
        # Create a filter form
        form = forms.BGPRoutingInstanceFilterForm()

        # Verify the form has a VRF field
        self.assertIn("vrf", form.fields)

        # Test that the field is a DynamicModelMultipleChoiceField
        self.assertIsInstance(form.fields["vrf"], forms.DynamicModelMultipleChoiceField)

        # Test that the field's queryset includes our VRFs
        self.assertIn(self.vrf_red, form.fields["vrf"].queryset)
        self.assertIn(self.vrf_blue, form.fields["vrf"].queryset)

    def test_bgp_routing_instance_bulk_edit_form_vrf_field(self):
        """Test VRF field in BGPRoutingInstanceBulkEditForm."""
        # Create a bulk edit form
        form = forms.BGPRoutingInstanceBulkEditForm(model=models.BGPRoutingInstance)

        # Verify the form has a VRF field
        self.assertIn("vrf", form.fields)

        # Test that the field is a DynamicModelChoiceField
        self.assertIsInstance(form.fields["vrf"], forms.DynamicModelChoiceField)

        # Test that vrf is in nullable_fields
        self.assertIn("vrf", form.Meta.nullable_fields)

    def test_peer_group_filter_form_vrf_field(self):
        """Test VRF field in PeerGroupFilterForm."""
        # Create a filter form
        form = forms.PeerGroupFilterForm()

        # Verify the form has a VRF field
        self.assertIn("vrf", form.fields)

        # Test that the field is a DynamicModelMultipleChoiceField
        self.assertIsInstance(form.fields["vrf"], forms.DynamicModelMultipleChoiceField)

    def test_address_family_form_vrf_field(self):
        """Test VRF field in AddressFamilyForm."""
        # Create a form
        form = forms.AddressFamilyForm()

        # Verify the form has a VRF field
        self.assertIn("vrf", form.fields)

        # Test that the field is a DynamicModelChoiceField
        self.assertIsInstance(form.fields["vrf"], forms.DynamicModelChoiceField)

    def test_address_family_filter_form_vrf_field(self):
        """Test VRF field in AddressFamilyFilterForm."""
        # Create a filter form
        form = forms.AddressFamilyFilterForm()

        # Verify the form has a VRF field
        self.assertIn("vrf", form.fields)

        # Test that the field is a DynamicModelMultipleChoiceField
        self.assertIsInstance(form.fields["vrf"], forms.DynamicModelMultipleChoiceField)

    def test_bgp_routing_instance_filterset_vrf_filter(self):
        """Test VRF filter in BGPRoutingInstanceFilterSet."""
        # Test filtering by VRF name
        filterset = filters.BGPRoutingInstanceFilterSet({"vrf": [self.vrf_red.name]})
        self.assertIn(self.bgp_instance_red, filterset.qs)
        self.assertNotIn(self.bgp_instance_blue, filterset.qs)
        self.assertNotIn(self.bgp_instance_no_vrf, filterset.qs)

    def test_peer_group_filterset_vrf_filter(self):
        """Test VRF filter in PeerGroupFilterSet."""
        # Test filtering by VRF
        filterset = filters.PeerGroupFilterSet({"vrf": [self.vrf_red.name]})
        self.assertIn(self.peer_group_red, filterset.qs)
        self.assertNotIn(self.peer_group_blue, filterset.qs)
        self.assertNotIn(self.peer_group_no_vrf, filterset.qs)

    def test_address_family_filterset_vrf_filter(self):
        """Test VRF filter in AddressFamilyFilterSet."""
        # Test filtering by VRF
        filterset = filters.AddressFamilyFilterSet({"vrf": [self.vrf_red.name]})
        self.assertIn(self.address_family_red, filterset.qs)
        self.assertNotIn(self.address_family_blue, filterset.qs)
        self.assertNotIn(self.address_family_no_vrf, filterset.qs)
