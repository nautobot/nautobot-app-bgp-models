"""Unit tests for nautobot_bgp_models."""  # pylint: disable=too-many-lines

from unittest import skip
from rest_framework import status
from django.test import override_settings

from django.contrib.contenttypes.models import ContentType

from nautobot.circuits.models import Provider
from nautobot.dcim.choices import InterfaceTypeChoices
from nautobot.dcim.models import Device, DeviceType, Interface, Manufacturer, Location, LocationType
from nautobot.extras.models import Status, Role, Tag
from nautobot.ipam.models import IPAddress, VRF, Prefix, Namespace
from nautobot.apps.testing import APIViewTestCases
from nautobot.users.models import ObjectPermission

from nautobot_bgp_models import models

from nautobot_bgp_models import choices


class AutonomousSystemAPITestCase(APIViewTestCases.APIViewTestCase):
    """Test the AutonomousSystem API."""

    model = models.AutonomousSystem
    view_namespace = "plugins-api:nautobot_bgp_models"
    bulk_update_data = {
        "description": "Reserved for use in documentation/sample code",
    }
    choices_fields = []

    # Nautobot testing doesn't correctly handle the API representation of a Status as a slug instead of a PK yet.
    validation_excluded_fields = ["status"]

    @classmethod
    def setUpTestData(cls):
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

        cls.create_data = [
            {"asn": 64496, "status": status_active.pk},
            {"asn": 65551, "status": status_active.pk},
            {"asn": 4294967294, "status": status_active.pk, "description": "Reserved for private use"},
        ]


class PeerGroupTemplateAPITestCase(APIViewTestCases.APIViewTestCase):
    """Test the PeerGroupTemplate API."""

    model = models.PeerGroupTemplate
    view_namespace = "plugins-api:nautobot_bgp_models"

    # TODO(mzb): Fix bulk update via #96 - ViewSets migration
    # bulk_update_data = {
    # }

    choices_fields = []

    @classmethod
    def setUpTestData(cls):
        status_active = Status.objects.get(name__iexact="active")
        status_active.content_types.add(ContentType.objects.get_for_model(models.AutonomousSystem))

        # Marek's ex ASes
        asn_5616 = models.AutonomousSystem.objects.create(asn=5616, status=status_active, description="ex Mediatel AS!")
        asn_8545 = models.AutonomousSystem.objects.create(asn=8545, status=status_active, description="Hi ex PL-IX AS!")

        peeringrole_int = Role.objects.create(name="Internal", color="333333")
        peeringrole_int.content_types.add(ContentType.objects.get_for_model(models.PeerGroupTemplate))

        peeringrole_ext = Role.objects.create(name="External", color="333334")
        peeringrole_ext.content_types.add(ContentType.objects.get_for_model(models.PeerGroupTemplate))

        cls.create_data = [
            {
                "name": "Parent Peer Group Template 1",
                "enabled": True,
                "role": peeringrole_int.pk,
                "description": "Marek was here",
                "autonomous_system": asn_5616.pk,
                "extra_attributes": {"key1": 1, "key2": {"nested_key2": "nested_value2", "nk2": 2}},
            },
        ]

        cls.update_data = {
            "name": "Parent Peer Group Template 1 - modified",
            "enabled": False,
            "role": peeringrole_ext.pk,
            "description": "Marek was here",
            "autonomous_system": asn_8545.pk,
            "extra_attributes": {"key1": 2},
        }

        # PGT1 re-used by subsequent test-cases.
        models.PeerGroupTemplate.objects.create(
            name="PGT1",
            autonomous_system=asn_5616,
            enabled=True,
            extra_attributes={"key1": 1, "key2": {"nested_key2": "nested_value2", "nk2": 2}},
        )
        models.PeerGroupTemplate.objects.create(
            name="PGT2",
            enabled=True,
            autonomous_system=asn_8545,
            extra_attributes={"key1": 2},
        )
        models.PeerGroupTemplate.objects.create(
            name="PGT3",
            enabled=False,
            autonomous_system=asn_8545,
            extra_attributes={"key3": 3},
        )

    @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
    def test_peer_group_template_extra_attributes(self):
        """Test PeerGroup's inheritance path for extra attributes."""
        instance = models.PeerGroupTemplate.objects.get(name="PGT1")
        url = self._get_detail_url(instance)

        # Add object-level permission
        obj_perm = ObjectPermission(
            name="Test permission",
            constraints={"pk": instance.pk},
            actions=["view"],
        )
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ContentType.objects.get_for_model(self.model))

        pgt1_ea = {"key1": 1, "key2": {"nested_key2": "nested_value2", "nk2": 2}}

        # URLs tested. In each case, PeerGroupTemplate extra attribute should be the same.
        # PeerGroupTemplate does not support include_inherited filter param.
        # TODO(mzb): add negative test case for not-supported include_inherited.
        response = self.client.get(url, **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        extra_attrs = dict(response.data["extra_attributes"])

        # Ensure extra_attributes are as on the model
        self.assertEqual(extra_attrs, pgt1_ea)


class BGPRoutingInstanceAPITestCase(APIViewTestCases.APIViewTestCase):
    """Test the BGPRoutingInstance API."""

    model = models.BGPRoutingInstance
    view_namespace = "plugins-api:nautobot_bgp_models"
    bulk_update_data = {
        "description": "Glenn was here.",
    }

    choices_fields = []

    # Nautobot testing doesn't correctly handle the API representation of a Status as a slug instead of a PK yet.
    validation_excluded_fields = ["status"]

    @classmethod
    def setUpTestData(cls):  # pylint: disable=too-many-locals
        status_active = Status.objects.get(name__iexact="active")
        status_active.content_types.add(ContentType.objects.get_for_model(models.AutonomousSystem))
        status_active.content_types.add(ContentType.objects.get_for_model(models.BGPRoutingInstance))
        tag = Tag.objects.create(name="Gerasimos Tag")
        tag.content_types.add(ContentType.objects.get_for_model(models.BGPRoutingInstance))

        manufacturer = Manufacturer.objects.create(name="Cisco")
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model="CSR 1000V")
        location_type = LocationType.objects.create(name="site")
        location_status = Status.objects.get_for_model(Location).first()
        location = Location.objects.create(name="Site 1", location_type=location_type, status=location_status)
        devicerole = Role.objects.create(name="Router", color="ff0000")
        devicerole.content_types.add(ContentType.objects.get_for_model(Device))
        device_1 = Device.objects.create(
            device_type=devicetype, role=devicerole, name="Device 1", location=location, status=status_active
        )
        device_2 = Device.objects.create(
            device_type=devicetype, role=devicerole, name="Device 2", location=location, status=status_active
        )
        device_3 = Device.objects.create(
            device_type=devicetype, role=devicerole, name="Device 3", location=location, status=status_active
        )
        device_4 = Device.objects.create(
            device_type=devicetype, role=devicerole, name="Device 4", location=location, status=status_active
        )

        vrf = VRF.objects.create(name="Ark B")

        interface_status = Status.objects.get_for_model(Interface).first()
        interface = Interface.objects.create(
            device=device_1,
            name="Loopback1",
            type=InterfaceTypeChoices.TYPE_VIRTUAL,
            status=interface_status,
            vrf=vrf,
        )

        namespace = Namespace.objects.first()
        prefix_status = Status.objects.get_for_model(Prefix).first()
        Prefix.objects.create(prefix="10.0.0.0/8", namespace=namespace, status=prefix_status)

        address = IPAddress.objects.create(address="10.1.1.1/24", status=status_active, namespace=namespace)

        interface.add_ip_addresses(address)

        # Marek's ex ASes
        asn_5616 = models.AutonomousSystem.objects.create(asn=5616, status=status_active, description="ex Mediatel AS!")

        asn_8545 = models.AutonomousSystem.objects.create(asn=8545, status=status_active, description="Hi ex PL-IX AS!")

        asn_15521 = models.AutonomousSystem.objects.create(
            asn=15521, status=status_active, description="Hi ex Premium Internet AS!"
        )

        cls.create_data = [
            {
                "description": "Hello World!",
                "autonomous_system": asn_8545.pk,
                "device": device_1.pk,
                "router_id": address.pk,
                "extra_attributes": {"key1": 1, "key2": {"nested_key2": "nested_value2", "nk2": 2}},
                "status": status_active.pk,
                "tags": [tag.pk],
            },
        ]

        cls.update_data = {
            "description": "Hello World!!!",
            "extra_attributes": '{"key1": "value1"}',
            "router_id": None,
        }

        models.BGPRoutingInstance.objects.create(
            device=device_2,
            autonomous_system=asn_5616,
            extra_attributes={"key1": 1, "key2": {"nested_key2": "nested_value2", "nk2": 2}},
            status=status_active,
        )
        models.BGPRoutingInstance.objects.create(
            device=device_3,
            autonomous_system=asn_8545,
            status=status_active,
        )
        models.BGPRoutingInstance.objects.create(
            device=device_4,
            autonomous_system=asn_15521,
            status=status_active,
        )

        cls.maxDiff = None

    @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
    def test_bgp_routing_instance_extra_attributes(self):
        """Test PeerGroup's inheritance path for extra attributes."""
        instance = models.BGPRoutingInstance.objects.get(device__name="Device 2")
        url = self._get_detail_url(instance)

        # Add object-level permission
        obj_perm = ObjectPermission(
            name="Test permission",
            constraints={"pk": instance.pk},
            actions=["view"],
        )
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ContentType.objects.get_for_model(self.model))

        device_2_extra_attributes = {"key1": 1, "key2": {"nested_key2": "nested_value2", "nk2": 2}}

        # URLs tested. In each case, BGPRoutingInstance extra attribute should be the same.
        # PeerGroupTemplate does not support include_inherited filter param.
        # TODO(mzb): add negative test case for not-supported include_inherited.
        response = self.client.get(url, **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        extra_attrs = dict(response.data["extra_attributes"])

        # Ensure extra_attributes are as on the model
        self.assertEqual(extra_attrs, device_2_extra_attributes)

    @skip("Not implemented")
    def test_notes_url_on_object(self):
        pass


class PeerGroupAPITestCase(APIViewTestCases.APIViewTestCase):
    """Test the PeerGroup API.

    TODO(mzb): Add unittests: prevent changing related BGP Routing Instance.
    """

    model = models.PeerGroup
    view_namespace = "plugins-api:nautobot_bgp_models"
    bulk_update_data = {
        "description": "Glenn was here.",
        "enabled": True,
        "autonomous_system": None,
    }

    # Nautobot testing doesn't correctly handle the API representation of a Status as a slug instead of a PK yet.
    validation_excluded_fields = ["status"]

    choices_fields = []

    @classmethod
    def setUpTestData(cls):  # pylint: disable=too-many-locals
        status_active = Status.objects.get(name__iexact="active")
        status_active.content_types.add(ContentType.objects.get_for_model(models.AutonomousSystem))

        manufacturer = Manufacturer.objects.create(name="Cisco")
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model="CSR 1000V")
        location_type = LocationType.objects.create(name="site")
        location_status = Status.objects.get_for_model(Location).first()
        location = Location.objects.create(name="Site 1", location_type=location_type, status=location_status)
        devicerole = Role.objects.create(name="Router", color="ff0000")
        devicerole.content_types.add(ContentType.objects.get_for_model(Device))
        device = Device.objects.create(
            device_type=devicetype, role=devicerole, name="Device 1", location=location, status=status_active
        )

        vrf = VRF.objects.create(name="Ark B")

        interface_status = Status.objects.get_for_model(Interface).first()
        interface = Interface.objects.create(
            device=device,
            name="Loopback1",
            type=InterfaceTypeChoices.TYPE_VIRTUAL,
            status=interface_status,
            vrf=vrf,
        )

        namespace = Namespace.objects.first()
        prefix_status = Status.objects.get_for_model(Prefix).first()
        prefix = Prefix.objects.create(prefix="10.0.0.0/8", namespace=namespace, status=prefix_status)
        vrf.prefixes.add(prefix)

        address = IPAddress.objects.create(address="10.1.1.1/24", status=status_active, namespace=namespace)

        interface.add_ip_addresses(address)

        peeringrole = Role.objects.create(name="Internal", color="333333")
        peeringrole.content_types.add(ContentType.objects.get_for_model(models.PeerGroup))

        external_peeringrole = Role.objects.create(name="External", color="333334")
        external_peeringrole.content_types.add(ContentType.objects.get_for_model(models.PeerGroup))

        asn_15521 = models.AutonomousSystem.objects.create(
            asn=15521, status=status_active, description="Hi ex Premium Internet AS!"
        )

        asn_8545 = models.AutonomousSystem.objects.create(asn=8545, status=status_active, description="Hi ex PL-IX AS!")

        bgp_routing_instance = models.BGPRoutingInstance.objects.create(
            description="Hello World!",
            autonomous_system=asn_8545,
            device=device,
            extra_attributes={"ri_key": "ri_value", "ri_nk": {"ri_nk": "ri_nv", "ri_nk2": "ri_nv2"}},
            status=status_active,
        )

        cls.create_data = [
            {
                "name": "Group A",
                "routing_instance": bgp_routing_instance.pk,
                "autonomous_system": asn_15521.pk,
                "role": peeringrole.pk,
                "description": "Telephone sanitizers",
                "enabled": True,
                "source_ip": address.pk,
                "vrf": vrf.pk,
            },
            {
                "name": "Group B",
                "routing_instance": bgp_routing_instance.pk,
                "role": peeringrole.pk,
                "extra_attributes": {"key1": 1, "key2": {"nested_key2": "nested_value2", "nk2": 2}},
            },
            {
                "name": "Group C",
                "routing_instance": bgp_routing_instance.pk,
                "role": peeringrole.pk,
                "enabled": False,
            },
        ]

        cls.update_data = {
            "name": "Updated Group A",
            "role": external_peeringrole.pk,
            "description": "Updated telephone sanitizers",
            "enabled": False,
            "autonomous_system": asn_8545.pk,
            "source_ip": None,
            "source_interface": interface.pk,
            "vrf": vrf.pk,
            "extra_attributes": '{"key1": "value1", "key2": {"nested_key2": "nested_value2"}}',
        }
        pgt1 = models.PeerGroupTemplate.objects.create(
            name="PGT1",
            extra_attributes={"pgt1_key": "pgt1_value"},
        )

        # Note: PeerGroup "Group 1" re-used in subsequent inheritance test-cases.
        models.PeerGroup.objects.create(
            name="Group 1",
            role=peeringrole,
            routing_instance=bgp_routing_instance,
            extra_attributes={"pg_key": "pg_value", "ri_nk": {"pg_nk": "pg_nv", "ri_nk2": "pg_nv2"}},
            peergroup_template=pgt1,
        )

        models.PeerGroup.objects.create(name="Group 2", role=peeringrole, routing_instance=bgp_routing_instance)

        models.PeerGroup.objects.create(name="Group 3", role=peeringrole, routing_instance=bgp_routing_instance)

        cls.maxDiff = None

    @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
    def test_peergroup_inherits_extra_attributes(self):
        """Test PeerGroup's inheritance path for extra attributes."""
        instance = models.PeerGroup.objects.get(name="Group 1")
        url = self._get_detail_url(instance)

        # Add object-level permission
        obj_perm = ObjectPermission(
            name="Test permission",
            constraints={"pk": instance.pk},
            actions=["view"],
        )
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ContentType.objects.get_for_model(self.model))

        urls = [
            f"{url}?include_inherited=true",
            f"{url}?include_inherited=True",
            f"{url}?include_inherited=1",
        ]

        for _url in urls:
            response = self.client.get(_url, **self.header)

            self.assertHttpStatus(response, status.HTTP_200_OK)
            api_extra_attrs = dict(response.data["extra_attributes"])

            # BGPRoutingInstance extra_attrs: {"ri_key": "ri_value", "ri_nk": {"ri_nk": "ri_nv", "ri_nk2": "ri_nv2"}}
            # PeerGroup's extra_attrs: {"pg_key": "pg_value", "ri_nk": {"pg_nk": "pg_nv", "ri_nk2": "pg_nv2"}},
            # pgt1_extra_attributes = {"pgt1_key": "pgt1_value"},

            # Ensure extra_attributes are deep-merged
            self.assertEqual(
                api_extra_attrs,
                {
                    "ri_key": "ri_value",  # Root-inherited from BGP RI
                    "pgt1_key": "pgt1_value",  # Root-inherited from PeerGroupTemplate
                    "pg_key": "pg_value",  # Root-added by PeerGroup
                    "ri_nk": {
                        "pg_nk": "pg_nv",  # Deep-added by PeerGroup
                        "ri_nk": "ri_nv",  # Deep-Inherited from BGP RI
                        "ri_nk2": "pg_nv2",  # Deep-Overriden from BGP RI
                    },
                },
            )

    @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
    def test_peergroup_owns_extra_attributes(self):
        """Test PeerGroup's inheritance path for extra attributes."""
        instance = models.PeerGroup.objects.get(name="Group 1")
        url = self._get_detail_url(instance)

        # Add object-level permission
        obj_perm = ObjectPermission(
            name="Test permission",
            constraints={"pk": instance.pk},
            actions=["view"],
        )
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ContentType.objects.get_for_model(self.model))

        urls = [
            f"{url}?include_inherited=false",
            f"{url}?include_inherited=False",
            f"{url}?include_inherited=0",
            f"{url}",
        ]

        for _url in urls:
            response = self.client.get(_url, **self.header)

            self.assertHttpStatus(response, status.HTTP_200_OK)
            api_extra_attrs = dict(response.data["extra_attributes"])
            pg_extra_attrs = {"pg_key": "pg_value", "ri_nk": {"pg_nk": "pg_nv", "ri_nk2": "pg_nv2"}}

            # Ensure extra_attributes are not deep-merged and returned as defined on the model instance.
            self.assertEqual(api_extra_attrs, pg_extra_attrs)

    @skip("Not implemented")
    def test_notes_url_on_object(self):
        pass

    # @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
    # def test_get_object_include_inherited(self):
    #     """Test object retrieval with the `include_inherited` flag."""
    #     instance = self._get_queryset()[0]
    #
    #     # Add object-level permission
    #     obj_perm = ObjectPermission(
    #         name="Test permission",
    #         constraints={"pk": instance.pk},
    #         actions=["view"],
    #     )
    #     obj_perm.save()
    #     obj_perm.users.add(self.user)
    #     obj_perm.object_types.add(ContentType.objects.get_for_model(self.model))
    #
    #     url = self._get_detail_url(instance)
    #     response = self.client.get(url, **self.header)
    #     self.assertHttpStatus(response, status.HTTP_200_OK)
    #     # # Properties not set on the instance
    #     # self.assertIsNone(response.data["autonomous_system"])
    #     # self.assertIsNone(response.data["router_id"])


class PeerEndpointAPITestCase(APIViewTestCases.APIViewTestCase):
    """Test the PeerEndpoint API."""

    model = models.PeerEndpoint
    view_namespace = "plugins-api:nautobot_bgp_models"

    bulk_update_data = {
        "enabled": False,
    }

    # Nautobot testing doesn't correctly handle the API representation of a Status as a slug instead of a PK yet.
    validation_excluded_fields = ["status"]

    choices_fields = []

    @skip("PeerEndpoint updates two objects")
    def test_update_object(self):
        pass

    @skip("PeerEndpoint creates two objects")
    def test_create_object(self):
        pass

    @skip("PeerEndpoint creates two objects")
    def test_recreate_object_csv(self):
        pass

    @classmethod
    def setUpTestData(cls):
        cls.status_active = Status.objects.get(name__iexact="active")
        cls.status_active.content_types.add(ContentType.objects.get_for_model(models.AutonomousSystem))
        cls.status_active.content_types.add(ContentType.objects.get_for_model(models.Peering))

        cls.peeringrole = Role.objects.create(name="Internal", color="333333")
        cls.peeringrole.content_types.add(ContentType.objects.get_for_model(models.PeerEndpoint))

        cls.peering = (
            models.Peering.objects.create(
                status=cls.status_active,
            ),
            models.Peering.objects.create(
                status=cls.status_active,
            ),
            models.Peering.objects.create(
                status=cls.status_active,
            ),
            models.Peering.objects.create(
                status=cls.status_active,
            ),
        )

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
            status=cls.status_active,
        )
        interface_status = Status.objects.get_for_model(Interface).first()
        interface = Interface.objects.create(
            device=device,
            name="Loopback1",
            type=InterfaceTypeChoices.TYPE_VIRTUAL,
            status=interface_status,
        )

        # cls.vrf = VRF.objects.create(name="Ark B")

        namespace = Namespace.objects.first()
        prefix_status = Status.objects.get_for_model(Prefix).first()
        Prefix.objects.create(prefix="10.0.0.0/8", namespace=namespace, status=prefix_status)

        cls.addresses = (
            IPAddress.objects.create(
                address="10.1.1.1/24",
                status=cls.status_active,
                namespace=namespace,
            ),
            IPAddress.objects.create(
                address="10.1.2.1/24",
                status=cls.status_active,
                namespace=namespace,
            ),
            IPAddress.objects.create(
                address="10.1.3.1/24",
                status=cls.status_active,
                namespace=namespace,
            ),
            IPAddress.objects.create(
                address="10.10.1.1/24",
                status=cls.status_active,
                namespace=namespace,
            ),
            IPAddress.objects.create(
                address="10.10.2.1/24",
                status=cls.status_active,
                namespace=namespace,
            ),
            IPAddress.objects.create(
                address="10.10.3.1/24",
                status=cls.status_active,
                namespace=namespace,
            ),
        )

        interface.add_ip_addresses([cls.addresses[0], cls.addresses[1], cls.addresses[2]])

        cls.asn = models.AutonomousSystem.objects.create(asn=4294967294, status=cls.status_active)

        provider = Provider.objects.create(name="Provider")
        cls.provider_asn = models.AutonomousSystem.objects.create(
            asn=15521,
            status=cls.status_active,
            provider=provider,
        )

        cls.bgp_routing_instance = models.BGPRoutingInstance.objects.create(
            description="Hello World!",
            autonomous_system=cls.asn,
            device=device,
            status=cls.status_active,
        )

        cls.pgt1 = models.PeerGroupTemplate.objects.create(
            name="PGT1",
            extra_attributes={"pgt_key": "pgt_value"},
        )

        peergroup = models.PeerGroup.objects.create(
            name="Group 1",
            role=cls.peeringrole,
            routing_instance=cls.bgp_routing_instance,
            peergroup_template=cls.pgt1,
            extra_attributes={"pg_key": "pg_value"},
            # vrf=cls.vrf,
            # router_id=cls.addresses[3],
            # autonomous_system=cls.asn,
        )

        # Peering #0
        cls.pe = models.PeerEndpoint.objects.create(
            routing_instance=cls.bgp_routing_instance,
            source_ip=cls.addresses[0],
            peer_group=peergroup,
            peering=cls.peering[0],
            extra_attributes={"pe_key": "pe_value"},
        )
        models.PeerEndpoint.objects.create(
            source_ip=cls.addresses[3],
            autonomous_system=cls.provider_asn,
            peering=cls.peering[0],
        )

        # Peering #3
        models.PeerEndpoint.objects.create(
            routing_instance=cls.bgp_routing_instance,
            source_ip=cls.addresses[2],
            autonomous_system=cls.provider_asn,
            peering=cls.peering[3],
        )
        models.PeerEndpoint.objects.create(
            source_ip=cls.addresses[3],
            autonomous_system=cls.provider_asn,
            peering=cls.peering[3],
        )

        cls.create_data = [
            # Peering #1
            {
                "source_ip": cls.addresses[1].pk,
                "routing_instance": cls.bgp_routing_instance.pk,
                "peer_group": peergroup.pk,
                "peering": cls.peering[1].pk,
            },
            {
                "source_ip": cls.addresses[4].pk,
                "autonomous_system": cls.provider_asn.pk,
                "peering": cls.peering[1].pk,
            },
        ]

        cls.maxDiff = None

    @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
    def test_peerendpoint_inherits_extra_attributes(self):
        """Test PeerEndpoint's inheritance path for extra attributes."""
        instance = self.pe
        url = self._get_detail_url(instance)

        # Add object-level permission
        obj_perm = ObjectPermission(
            name="Test permission",
            constraints={"pk": instance.pk},
            actions=["view"],
        )
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ContentType.objects.get_for_model(self.model))

        urls = [
            f"{url}?include_inherited=true",
            f"{url}?include_inherited=True",
            f"{url}?include_inherited=1",
        ]

        for _url in urls:
            response = self.client.get(_url, **self.header)

            self.assertHttpStatus(response, status.HTTP_200_OK)
            api_extra_attrs = dict(response.data["extra_attributes"])
            inherited_extra_attrs = {
                "pe_key": "pe_value",
                "pg_key": "pg_value",
                "pgt_key": "pgt_value",
            }
            # Ensure extra_attributes are deep-merged
            self.assertEqual(api_extra_attrs, inherited_extra_attrs)

    @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
    def test_peerendpoint_owns_extra_attributes(self):
        """Test PeerEndpoint's inheritance path for extra attributes."""
        instance = self.pe
        url = self._get_detail_url(instance)

        # Add object-level permission
        obj_perm = ObjectPermission(
            name="Test permission",
            constraints={"pk": instance.pk},
            actions=["view"],
        )
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ContentType.objects.get_for_model(self.model))

        urls = [
            f"{url}?include_inherited=false",
            f"{url}?include_inherited=False",
            f"{url}?include_inherited=0",
            f"{url}",
        ]

        for _url in urls:
            response = self.client.get(_url, **self.header)

            self.assertHttpStatus(response, status.HTTP_200_OK)
            api_extra_attrs = dict(response.data["extra_attributes"])
            # Extra attrs defined on the cls.pe. (class' peerendpoint)
            pe_extra_attrs = {"pe_key": "pe_value"}

            # Ensure extra_attributes are not deep-merged and returned as defined on the model instance.
            self.assertEqual(api_extra_attrs, pe_extra_attrs)


#     @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
#     def test_get_object_include_inherited(self):
#         """Test object retrieval with the `include_inherited` flag."""
#         instance = self._get_queryset()[0]
#
#         # Add object-level permission
#         obj_perm = ObjectPermission(
#             name="Test permission",
#             constraints={"pk": instance.pk},
#             actions=["view"],
#         )
#         obj_perm.save()
#         obj_perm.users.add(self.user)
#         obj_perm.object_types.add(ContentType.objects.get_for_model(self.model))
#
#         # Retrieve without inheritance
#         url = self._get_detail_url(instance)
#         response = self.client.get(url, **self.header)
#         self.assertHttpStatus(response, status.HTTP_200_OK)
#         # Properties not set on the instance
#         self.assertIsNone(response.data["autonomous_system"])
#         self.assertIsNone(response.data["router_id"])
#
#         # Retrieve with inheritance
#         url = self._get_detail_url(instance)
#         response = self.client.get(f"{url}?include_inherited", **self.header)
#         self.assertHttpStatus(response, status.HTTP_200_OK)
#         # Properties not set on the instance but inheritable from the parent peer-group
#         self.assertEqual(self.asn.pk, response.data["autonomous_system"])
#         self.assertEqual(self.addresses[3].pk, response.data["router_id"])
#
#         # Retrieve with explictly excluded inheritance
#         url = self._get_detail_url(instance)
#         response = self.client.get(f"{url}?include_inherited=false", **self.header)
#         self.assertHttpStatus(response, status.HTTP_200_OK)
#         self.assertIsNone(response.data["autonomous_system"])
#         self.assertIsNone(response.data["router_id"])
#
#     def test_invalid_combinations(self):
#         """Test various invalid combinations of parameters."""
#         obj_perm = ObjectPermission(name="Test permission", actions=["add"])
#         obj_perm.save()
#         obj_perm.users.add(self.user)
#         obj_perm.object_types.add(ContentType.objects.get_for_model(self.model))
#
#         for data, error_key, error_str in (
#             (
#                 # Mismatch between local IP's assigned VRF and the explicitly specified VRF
#                 {
#                     "local_ip": self.addresses[0].pk,
#                     "vrf": VRF.objects.create(name="other_vrf").pk,
#                     "peering": self.peering[2].pk,
#                 },
#                 "__all__",
#                 "VRF other_vrf was specified, but one or more attributes refer instead to Ark B",
#             ),
#         ):
#             response = self.client.post(self._get_list_url(), data, format="json", **self.header)
#             self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)
#             self.assertIn(error_key, response.data)
#             self.assertIn(error_str, str(response.data[error_key][0]))
#
#         # TODO: lots more negative test possibilities here...


class PeeringAPITestCase(APIViewTestCases.APIViewTestCase):
    """Test the Peering API."""

    model = models.Peering
    view_namespace = "plugins-api:nautobot_bgp_models"
    choices_fields = []

    # Nautobot testing doesn't correctly handle the API representation of a Status as a slug instead of a PK yet.
    # Nautobot testing also doesn't correctly handle the reverse-relation that is "endpoints"
    validation_excluded_fields = ["status", "endpoints"]

    @classmethod
    def setUpTestData(cls):
        status_active = Status.objects.get(name__iexact="active")
        status_active.content_types.add(ContentType.objects.get_for_model(models.Peering))

        namespace = Namespace.objects.first()
        prefix_status = Status.objects.get_for_model(Prefix).first()
        Prefix.objects.create(prefix="10.0.0.0/8", namespace=namespace, status=prefix_status)

        addresses = (
            IPAddress.objects.create(address="10.1.1.1/24", status=status_active, namespace=namespace),
            IPAddress.objects.create(address="10.1.1.2/24", status=status_active, namespace=namespace),
            IPAddress.objects.create(address="10.1.2.2/24", status=status_active, namespace=namespace),
            IPAddress.objects.create(address="10.1.2.3/24", status=status_active, namespace=namespace),
            IPAddress.objects.create(address="10.1.3.3/24", status=status_active, namespace=namespace),
            IPAddress.objects.create(address="10.1.3.4/24", status=status_active, namespace=namespace),
            IPAddress.objects.create(address="10.1.1.100/24", status=status_active, namespace=namespace),
        )

        provider = Provider.objects.create(name="Provider")
        asn = models.AutonomousSystem.objects.create(asn=15521, status=status_active, provider=provider)

        # peeringrole_internal = models.PeeringRole.objects.create(name="Internal", slug="internal", color="333333")
        # peeringrole_external = models.PeeringRole.objects.create(name="External", slug="external", color="0000ff")

        peering_1 = models.Peering.objects.create(
            status=status_active,
        )
        peering_2 = models.Peering.objects.create(
            status=status_active,
        )
        peering_3 = models.Peering.objects.create(
            status=status_active,
        )
        peerendpoints = (
            models.PeerEndpoint.objects.create(source_ip=addresses[0], autonomous_system=asn, peering=peering_1),
            models.PeerEndpoint.objects.create(source_ip=addresses[1], autonomous_system=asn, peering=peering_1),
            models.PeerEndpoint.objects.create(source_ip=addresses[2], autonomous_system=asn, peering=peering_2),
            models.PeerEndpoint.objects.create(source_ip=addresses[3], autonomous_system=asn, peering=peering_2),
            models.PeerEndpoint.objects.create(source_ip=addresses[4], autonomous_system=asn, peering=peering_3),
            models.PeerEndpoint.objects.create(source_ip=addresses[5], autonomous_system=asn, peering=peering_3),
        )

        peerendpoints[0].peer = peerendpoints[1]
        peerendpoints[1].peer = peerendpoints[0]

        peerendpoints[2].peer = peerendpoints[3]
        peerendpoints[3].peer = peerendpoints[2]

        peerendpoints[4].peer = peerendpoints[5]
        peerendpoints[5].peer = peerendpoints[4]

        cls.create_data = [
            {
                "status": status_active.pk,
            },
            {
                "status": status_active.pk,
            },
            {
                "status": status_active.pk,
            },
        ]

        cls.bulk_update_data = {
            "status": status_active.pk,
        }


class AddressFamilyAPITestCase(APIViewTestCases.APIViewTestCase):
    """Test the AddressFamily API."""

    model = models.AddressFamily
    view_namespace = "plugins-api:nautobot_bgp_models"

    choices_fields = ["afi_safi"]

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
        device = Device.objects.create(
            device_type=devicetype,
            role=devicerole,
            name="Device 1",
            location=location,
            status=status_active,
        )

        asn_8545 = models.AutonomousSystem.objects.create(asn=8545, status=status_active, description="Hi ex PL-IX AS!")

        # provider = Provider.objects.create(name="Provider", slug="provider")
        # asn_15521 = models.AutonomousSystem.objects.create(
        #     asn=15521,
        #     status=status_active,
        #     description="Hi ex Premium Internet AS!",
        #     provider=provider,
        # )

        bgp_routing_instance = models.BGPRoutingInstance.objects.create(
            description="Hello World!",
            autonomous_system=asn_8545,
            device=device,
            status=status_active,
        )

        # interface_1 = Interface.objects.create(device=device, name="Loopback1", type=InterfaceTypeChoices.TYPE_VIRTUAL)
        # interface_2 = Interface.objects.create(device=device, name="Loopback2", type=InterfaceTypeChoices.TYPE_VIRTUAL)

        # addresses = (
        #     IPAddress.objects.create(
        #         address="10.1.1.1/24",
        #         assigned_object=interface_1,
        #         status=status_active,
        #     ),
        #     IPAddress.objects.create(
        #         address="10.1.1.2/24",
        #         status=status_active,
        #     ),
        # )

        # peeringrole = models.PeeringRole.objects.create(name="Internal", slug="internal", color="333333")
        # peergroup = models.PeerGroup.objects.create(
        #     name="Group 1",
        #     role=peeringrole,
        #     routing_instance=bgp_routing_instance,
        # )

        # peering = models.Peering.objects.create(status=status_active)
        # peerendpoint_1 = models.PeerEndpoint.objects.create(
        #     routing_instance=bgp_routing_instance,
        #     source_ip=addresses[0],
        #     peer_group=peergroup,
        #     peering=peering,
        # )
        # peerendpoint_2 = models.PeerEndpoint.objects.create(
        #     source_ip=addresses[1],
        #     autonomous_system=asn_15521,
        #     peering=peering,
        # )

        models.AddressFamily.objects.create(
            routing_instance=bgp_routing_instance,
            afi_safi=choices.AFISAFIChoices.AFI_IPV4_UNICAST,
        )
        models.AddressFamily.objects.create(
            routing_instance=bgp_routing_instance,
            afi_safi=choices.AFISAFIChoices.AFI_IPV6_UNICAST,
        )
        models.AddressFamily.objects.create(
            routing_instance=bgp_routing_instance,
            afi_safi=choices.AFISAFIChoices.AFI_IPV4_MULTICAST,
        )

        vrf = VRF.objects.create(name="New VRF")

        cls.create_data = [
            {
                "afi_safi": choices.AFISAFIChoices.AFI_IPV4_FLOWSPEC,
                "routing_instance": bgp_routing_instance.pk,
                "extra_attributes": {"key1": "value1"},
            },
            {
                "afi_safi": choices.AFISAFIChoices.AFI_VPNV4_UNICAST,
                "routing_instance": bgp_routing_instance.pk,
            },
            {
                "afi_safi": choices.AFISAFIChoices.AFI_VPNV6_UNICAST,
                "routing_instance": bgp_routing_instance.pk,
            },
        ]

        cls.bulk_update_data = {
            "vrf": vrf.pk,
        }


#     @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
#     def test_get_object_include_inherited(self):
#         """Test object retrieval with the `include_inherited` flag."""
#         instance = self._get_queryset().get(peer_endpoint__isnull=False)
#
#         # Add object-level permission
#         obj_perm = ObjectPermission(
#             name="Test permission",
#             constraints={"pk": instance.pk},
#             actions=["view"],
#         )
#         obj_perm.save()
#         obj_perm.users.add(self.user)
#         obj_perm.object_types.add(ContentType.objects.get_for_model(self.model))
#
#         # Retrieve without inheritance
#         url = self._get_detail_url(instance)
#         response = self.client.get(url, **self.header)
#         self.assertHttpStatus(response, status.HTTP_200_OK)
#         # TODO: Properties not set on the instance
#
#         # Retrieve with inheritance
#         url = self._get_detail_url(instance)
#         response = self.client.get(f"{url}?include_inherited", **self.header)
#         self.assertHttpStatus(response, status.HTTP_200_OK)
#         # TODO: Properties not set on the instance but inheritable from the parent address-families
#
#         # Retrieve with explictly excluded inheritance
#         url = self._get_detail_url(instance)
#         response = self.client.get(f"{url}?include_inherited=false", **self.header)
#         self.assertHttpStatus(response, status.HTTP_200_OK)
#         # TODO: Properties not set on the instance


class PeerGroupAddressFamilyAPITestCase(APIViewTestCases.APIViewTestCase):
    """Test the PeerGroupAddressFamily API."""

    model = models.PeerGroupAddressFamily
    view_namespace = "plugins-api:nautobot_bgp_models"
    choices_fields = ["afi_safi"]

    @classmethod
    def setUpTestData(cls):  # pylint: disable=too-many-locals
        status_active = Status.objects.get(name__iexact="active")
        status_active.content_types.add(ContentType.objects.get_for_model(models.AutonomousSystem))

        manufacturer = Manufacturer.objects.create(name="Cisco")
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model="CSR 1000V")

        location_type = LocationType.objects.create(name="site")
        location_status = Status.objects.get_for_model(Location).first()
        location = Location.objects.create(name="Site 1", location_type=location_type, status=location_status)
        devicerole = Role.objects.create(name="Router", color="ff0000")
        device = Device.objects.create(
            device_type=devicetype, role=devicerole, name="Device 1", location=location, status=status_active
        )

        asn_8545 = models.AutonomousSystem.objects.create(asn=8545, status=status_active, description="Hi ex PL-IX AS!")

        bgp_routing_instance = models.BGPRoutingInstance.objects.create(
            description="Hello World!",
            autonomous_system=asn_8545,
            device=device,
            extra_attributes={"ri_key": "ri_value", "ri_nk": {"ri_nk": "ri_nv", "ri_nk2": "ri_nv2"}},
            status=status_active,
        )

        peer_group_1 = models.PeerGroup.objects.create(
            name="Group A",
            routing_instance=bgp_routing_instance,
        )
        peer_group_2 = models.PeerGroup.objects.create(
            name="Group B",
            routing_instance=bgp_routing_instance,
        )

        models.PeerGroupAddressFamily.objects.create(
            peer_group=peer_group_2,
            afi_safi="ipv4_unicast",
            import_policy="IMPORT",
            export_policy="EXPORT",
            extra_attributes={"key1": 1},
        )
        models.PeerGroupAddressFamily.objects.create(
            peer_group=peer_group_2,
            afi_safi="ipv6_unicast",
        )
        models.PeerGroupAddressFamily.objects.create(
            peer_group=peer_group_2,
            afi_safi="vpnv4_unicast",
        )

        cls.create_data = [
            {
                "afi_safi": "ipv4_unicast",
                "peer_group": peer_group_1.pk,
                "import_policy": "IMPORT",
                "export_policy": "EXPORT",
                "multipath": True,
                "extra_attributes": {"key1": 1},
            },
            {
                "afi_safi": "ipv6_labeled_unicast",
                "peer_group": peer_group_1.pk,
            },
            {
                "afi_safi": "vpnv4_unicast",
                "peer_group": peer_group_1.pk,
            },
        ]

        cls.update_data = {
            "import_policy": "IMPORT_V2",
            "export_policy": "EXPORT_V2",
            "multipath": False,
            "extra_attributes": {"key2": 2},
        }


class PeerEndpointAddressFamilyAPITestCase(APIViewTestCases.APIViewTestCase):
    """Test the PeerEndpointAddressFamily API."""

    model = models.PeerEndpointAddressFamily
    view_namespace = "plugins-api:nautobot_bgp_models"
    choices_fields = ["afi_safi"]

    @classmethod
    def setUpTestData(cls):
        cls.status_active = Status.objects.get(name__iexact="active")
        cls.status_active.content_types.add(ContentType.objects.get_for_model(models.AutonomousSystem))
        cls.status_active.content_types.add(ContentType.objects.get_for_model(models.Peering))

        namespace = Namespace.objects.first()
        prefix_status = Status.objects.get_for_model(Prefix).first()
        Prefix.objects.create(prefix="10.0.0.0/8", namespace=namespace, status=prefix_status)

        cls.peeringrole = Role.objects.create(name="Internal", color="333333")
        cls.peeringrole.content_types.add(ContentType.objects.get_for_model(models.PeerGroup))

        cls.peering = (
            models.Peering.objects.create(
                status=cls.status_active,
            ),
            models.Peering.objects.create(
                status=cls.status_active,
            ),
        )

        manufacturer = Manufacturer.objects.create(name="Cisco")
        cls.devicetype = DeviceType.objects.create(manufacturer=manufacturer, model="CSR 1000V")
        location_type = LocationType.objects.create(name="site")
        location_status = Status.objects.get_for_model(Location).first()
        cls.location = Location.objects.create(name="Site 1", location_type=location_type, status=location_status)
        cls.devicerole = Role.objects.create(name="Router", color="ff0000")

        device = Device.objects.create(
            device_type=cls.devicetype,
            role=cls.devicerole,
            name="Device 1",
            location=cls.location,
            status=cls.status_active,
        )
        interface_status = Status.objects.get_for_model(Interface).first()
        interface = Interface.objects.create(
            device=device,
            name="Loopback1",
            type=InterfaceTypeChoices.TYPE_VIRTUAL,
            status=interface_status,
        )

        # cls.vrf = VRF.objects.create(name="Ark B")

        cls.addresses = (
            IPAddress.objects.create(
                address="10.1.1.1/24",
                status=cls.status_active,
                namespace=namespace,
            ),
            IPAddress.objects.create(
                address="10.1.2.1/24",
                status=cls.status_active,
                namespace=namespace,
            ),
            IPAddress.objects.create(
                address="10.1.3.1/24",
                status=cls.status_active,
                namespace=namespace,
            ),
            IPAddress.objects.create(
                address="10.10.1.1/24",
                status=cls.status_active,
                namespace=namespace,
            ),
            IPAddress.objects.create(
                address="10.10.2.1/24",
                status=cls.status_active,
                namespace=namespace,
            ),
            IPAddress.objects.create(
                address="10.10.3.1/24",
                status=cls.status_active,
                namespace=namespace,
            ),
        )

        interface.add_ip_addresses(
            [
                cls.addresses[0],
                cls.addresses[1],
                cls.addresses[2],
            ]
        )

        cls.asn = models.AutonomousSystem.objects.create(asn=4294967294, status=cls.status_active)

        provider = Provider.objects.create(name="Provider")
        cls.provider_asn = models.AutonomousSystem.objects.create(
            asn=15521,
            status=cls.status_active,
            provider=provider,
        )

        cls.bgp_routing_instance = models.BGPRoutingInstance.objects.create(
            description="Hello World!",
            autonomous_system=cls.asn,
            device=device,
            status=cls.status_active,
        )

        cls.pgt1 = models.PeerGroupTemplate.objects.create(
            name="PGT1",
            extra_attributes={"pgt_key": "pgt_value"},
        )

        peergroup = models.PeerGroup.objects.create(
            name="Group 1",
            role=cls.peeringrole,
            routing_instance=cls.bgp_routing_instance,
            peergroup_template=cls.pgt1,
            extra_attributes={"pg_key": "pg_value"},
            # vrf=cls.vrf,
            # router_id=cls.addresses[3],
            # autonomous_system=cls.asn,
        )

        cls.pes = [
            # Peering #0
            models.PeerEndpoint.objects.create(
                routing_instance=cls.bgp_routing_instance,
                source_ip=cls.addresses[0],
                peer_group=peergroup,
                peering=cls.peering[0],
                extra_attributes={"pe_key": "pe_value"},
            ),
            models.PeerEndpoint.objects.create(
                source_ip=cls.addresses[3],
                autonomous_system=cls.provider_asn,
                peering=cls.peering[0],
            ),
            # Peering #1
            models.PeerEndpoint.objects.create(
                routing_instance=cls.bgp_routing_instance,
                source_ip=cls.addresses[2],
                autonomous_system=cls.provider_asn,
                peering=cls.peering[1],
            ),
            models.PeerEndpoint.objects.create(
                source_ip=cls.addresses[3],
                autonomous_system=cls.provider_asn,
                peering=cls.peering[1],
            ),
        ]

        models.PeerEndpointAddressFamily.objects.create(
            peer_endpoint=cls.pes[0],
            afi_safi="ipv4_unicast",
        )
        models.PeerEndpointAddressFamily.objects.create(
            peer_endpoint=cls.pes[0],
            afi_safi="ipv6_unicast",
            import_policy="IMPORT",
            export_policy="EXPORT",
            multipath=True,
            extra_attributes={"key": "value"},
        )
        models.PeerEndpointAddressFamily.objects.create(
            peer_endpoint=cls.pes[2],
            afi_safi="ipv4_unicast",
        )

        cls.create_data = [
            {
                "peer_endpoint": cls.pes[0].pk,
                "afi_safi": "vpnv4_unicast",
                "import_policy": "IMPORT",
                "export_policy": "EXPORT",
                "multipath": False,
                "extra_attributes": {"KEY": "VALUE"},
            },
            {
                "peer_endpoint": cls.pes[1].pk,
                "afi_safi": "vpnv4_unicast",
            },
        ]
