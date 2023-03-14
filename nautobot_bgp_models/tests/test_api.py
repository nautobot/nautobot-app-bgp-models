"""Unit tests for nautobot_bgp_models."""
from unittest import skip

from django.contrib.contenttypes.models import ContentType
from nautobot.circuits.models import Provider
from nautobot.dcim.choices import InterfaceTypeChoices
from nautobot.dcim.models import Device, DeviceType, Interface, Manufacturer, Site
from nautobot.extras.models import Status, Role
from nautobot.ipam.models import IPAddress
from nautobot.apps.testing import APIViewTestCases

from nautobot_bgp_models import models
from nautobot_bgp_models import choices


class AutonomousSystemAPITestCase(APIViewTestCases.APIViewTestCase):
    """Test the AutonomousSystem API."""

    model = models.AutonomousSystem
    view_namespace = "plugins-api:nautobot_bgp_models"
    brief_fields = ["asn", "display", "id", "url"]
    bulk_update_data = {
        "description": "Reserved for use in documentation/sample code",
    }
    choices_fields = ["status"]

    # Nautobot testing doesn't correctly handle the API representation of a Status as a slug instead of a PK yet.
    validation_excluded_fields = ["status"]

    @classmethod
    def setUpTestData(cls):  # pylint: disable=invalid-name
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

        cls.create_data = [
            {"asn": 64496, "status": "active"},
            {"asn": 65551, "status": "active"},
            {"asn": 4294967294, "status": "active", "description": "Reserved for private use"},
        ]

    @skip("Not implemented")
    def test_notes_url_on_object(self):
        pass


class PeerGroupAPITestCase(APIViewTestCases.APIViewTestCase):
    """Test the PeerGroup API."""

    model = models.PeerGroup
    view_namespace = "plugins-api:nautobot_bgp_models"
    brief_fields = ["display", "enabled", "id", "name", "role", "url"]
    bulk_update_data = {
        "description": "Glenn was here.",
        "enabled": True,
        "autonomous_system": None,
    }

    # Nautobot testing doesn't correctly handle the API representation of a Status as a slug instead of a PK yet.
    validation_excluded_fields = ["status"]

    @classmethod
    def setUpTestData(cls):  # pylint: disable=invalid-name
        status_active = Status.objects.get(slug="active")
        status_active.content_types.add(ContentType.objects.get_for_model(models.AutonomousSystem))

        manufacturer = Manufacturer.objects.create(name="Cisco", slug="cisco")
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model="CSR 1000V", slug="csr1000v")
        site = Site.objects.create(name="Site 1", slug="site-1")
        devicerole = Role.objects.create(name="Router", slug="router", color="ff0000")
        devicerole.content_types.add(ContentType.objects.get_for_model(Device))
        device = Device.objects.create(
            device_type=devicetype, role=devicerole, name="Device 1", site=site, status=status_active
        )
        # interface = Interface.objects.create(device=device, name="Loopback1", type=InterfaceTypeChoices.TYPE_VIRTUAL)

        # vrf = VRF.objects.create(name="Ark B")
        # cls.address = IPAddress.objects.create(
        #     address="10.1.1.1/24", status=status_active, vrf=vrf, assigned_object=interface
        # )

        peeringrole = Role.objects.create(name="Internal", slug="internal", color="333333")
        peeringrole.content_types.add(ContentType.objects.get_for_model(models.PeerGroup))

        asn_15521 = models.AutonomousSystem.objects.create(
            asn=15521, status=status_active, description="Hi ex Premium Internet AS!"
        )

        asn_8545 = models.AutonomousSystem.objects.create(asn=8545, status=status_active, description="Hi ex PL-IX AS!")

        bgp_routing_instance = models.BGPRoutingInstance.objects.create(
            description="Hello World!",
            autonomous_system=asn_8545,
            device=device,
        )

        cls.create_data = [
            {
                "name": "Group A",
                "routing_instance": bgp_routing_instance.pk,
                "autonomous_system": asn_15521.pk,
                "role": peeringrole.pk,
                "description": "Telephone sanitizers",
                "enabled": True,
            },
            {
                "name": "Group B",
                "routing_instance": bgp_routing_instance.pk,
                "role": peeringrole.pk,
            },
            {
                "name": "Group C",
                "routing_instance": bgp_routing_instance.pk,
                "role": peeringrole.pk,
                "enabled": False,
            },
        ]

        # router_id_relation = Relationship.objects.get(slug="bgp_device_router_id")
        # RelationshipAssociation.objects.create(relationship=router_id_relation, source=device, destination=cls.address)

        # asn_relation = Relationship.objects.get(slug="bgp_asn")
        # RelationshipAssociation.objects.create(relationship=asn_relation, source=cls.asn, destination=device)

        models.PeerGroup.objects.create(name="Group 1", role=peeringrole, routing_instance=bgp_routing_instance)
        models.PeerGroup.objects.create(name="Group 2", role=peeringrole, routing_instance=bgp_routing_instance)
        models.PeerGroup.objects.create(name="Group 3", role=peeringrole, routing_instance=bgp_routing_instance)

        cls.maxDiff = None

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
    brief_fields = [
        "display",
        # "enabled",
        "id",
        # "local_ip",
        # "peer_group",
        "url",
    ]
    bulk_update_data = {
        "enabled": False,
    }

    # Nautobot testing doesn't correctly handle the API representation of a Status as a slug instead of a PK yet.
    validation_excluded_fields = ["status"]

    # TODO(mzb): Fix object changelog issue (2!=1)
    test_create_object = None

    @classmethod
    def setUpTestData(cls):  # pylint: disable=invalid-name
        cls.status_active = Status.objects.get(slug="active")
        cls.status_active.content_types.add(ContentType.objects.get_for_model(models.AutonomousSystem))
        cls.status_active.content_types.add(ContentType.objects.get_for_model(models.Peering))

        cls.peeringrole = Role.objects.create(name="Internal", slug="internal", color="333333")
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

        manufacturer = Manufacturer.objects.create(name="Cisco", slug="cisco")
        cls.devicetype = DeviceType.objects.create(manufacturer=manufacturer, model="CSR 1000V", slug="csr1000v")
        cls.site = Site.objects.create(name="Site 1", slug="site-1")
        cls.devicerole = Role.objects.create(name="Router", slug="router", color="ff0000")
        cls.devicerole.content_types.add(ContentType.objects.get_for_model(Device))
        device = Device.objects.create(
            device_type=cls.devicetype,
            role=cls.devicerole,
            name="Device 1",
            site=cls.site,
            status=cls.status_active,
        )
        interface = Interface.objects.create(device=device, name="Loopback1", type=InterfaceTypeChoices.TYPE_VIRTUAL)

        # cls.vrf = VRF.objects.create(name="Ark B")

        cls.addresses = (
            IPAddress.objects.create(
                address="10.1.1.1/24",
                status=cls.status_active,
                assigned_object=interface,
            ),
            IPAddress.objects.create(
                address="10.1.2.1/24",
                status=cls.status_active,
                assigned_object=interface,
            ),
            IPAddress.objects.create(
                address="10.1.3.1/24",
                status=cls.status_active,
                assigned_object=interface,
            ),
            IPAddress.objects.create(
                address="10.10.1.1/24",
                status=cls.status_active,
            ),
            IPAddress.objects.create(
                address="10.10.2.1/24",
                status=cls.status_active,
            ),
            IPAddress.objects.create(
                address="10.10.3.1/24",
                status=cls.status_active,
            ),
        )

        cls.asn = models.AutonomousSystem.objects.create(asn=4294967294, status=cls.status_active)

        provider = Provider.objects.create(name="Provider", slug="provider")
        cls.provider_asn = models.AutonomousSystem.objects.create(
            asn=15521,
            status=cls.status_active,
            provider=provider,
        )

        cls.bgp_routing_instance = models.BGPRoutingInstance.objects.create(
            description="Hello World!",
            autonomous_system=cls.asn,
            device=device,
        )

        peergroup = models.PeerGroup.objects.create(
            name="Group 1",
            role=cls.peeringrole,
            routing_instance=cls.bgp_routing_instance,
            # vrf=cls.vrf,
            # router_id=cls.addresses[3],
            # autonomous_system=cls.asn,
        )

        # Peering #0
        models.PeerEndpoint.objects.create(
            routing_instance=cls.bgp_routing_instance,
            source_ip=cls.addresses[0],
            peer_group=peergroup,
            peering=cls.peering[0],
        )
        models.PeerEndpoint.objects.create(
            source_ip=cls.addresses[3],
            autonomous_system=cls.provider_asn,
            peering=cls.peering[0],
        )
        models.PeerEndpoint.objects.create(
            source_ip=cls.addresses[2],
            autonomous_system=cls.provider_asn,
            peering=cls.peering[3],
        )
        # models.PeerEndpoint.objects.create(
        #     source_ip=cls.addresses[3],
        #     autonomous_system=cls.provider_asn,
        #     peering=cls.peering[3]
        # )

        # models.PeerEndpoint.objects.create(local_ip=cls.addresses[2], peer_group=peergroup, peering=cls.peering[1])

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
            {
                "source_ip": cls.addresses[2].pk,
                "routing_instance": cls.bgp_routing_instance.pk,
                "peer_group": peergroup.pk,
                "peering": cls.peering[1].pk,
            },
        ]

        cls.maxDiff = None

    @skip("Not implemented")
    def test_notes_url_on_object(self):
        pass


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
    brief_fields = ["display", "id", "status", "url"]
    choices_fields = ["status"]

    # Nautobot testing doesn't correctly handle the API representation of a Status as a slug instead of a PK yet.
    # Nautobot testing also doesn't correctly handle the reverse-relation that is "endpoints"
    validation_excluded_fields = ["status", "endpoints"]

    @classmethod
    def setUpTestData(cls):  # pylint: disable=invalid-name
        status_active = Status.objects.get(slug="active")
        status_active.content_types.add(ContentType.objects.get_for_model(models.Peering))

        addresses = (
            IPAddress.objects.create(address="10.1.1.1/24", status=status_active),
            IPAddress.objects.create(address="10.1.1.2/24", status=status_active),
            IPAddress.objects.create(address="10.1.2.2/24", status=status_active),
            IPAddress.objects.create(address="10.1.2.3/24", status=status_active),
            IPAddress.objects.create(address="10.1.3.3/24", status=status_active),
            IPAddress.objects.create(address="10.1.3.4/24", status=status_active),
            IPAddress.objects.create(address="10.1.1.100/24", status=status_active),
        )

        provider = Provider.objects.create(name="Provider", slug="provider")
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
                "status": "active",
            },
            {
                "status": "active",
            },
            {
                "status": "active",
            },
        ]

        cls.bulk_update_data = {
            "status": "provisioning",
        }

    @skip("Not implemented")
    def test_notes_url_on_object(self):
        pass


class AddressFamilyAPITestCase(APIViewTestCases.APIViewTestCase):
    """Test the AddressFamily API."""

    model = models.AddressFamily
    view_namespace = "plugins-api:nautobot_bgp_models"
    brief_fields = [
        "afi_safi",
        "display",
        "id",
        "url",
    ]
    choices_fields = ["afi_safi"]

    @classmethod
    def setUpTestData(cls):  # pylint: disable=too-many-locals, disable=invalid-name
        status_active = Status.objects.get(slug="active")
        manufacturer = Manufacturer.objects.create(name="Cisco", slug="cisco")
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model="CSR 1000V", slug="csr1000v")
        site = Site.objects.create(name="Site 1", slug="site-1")
        devicerole = Role.objects.create(name="Router", slug="router", color="ff0000")
        devicerole.content_types.add(ContentType.objects.get_for_model(Device))
        device = Device.objects.create(device_type=devicetype, role=devicerole, name="Device 1", site=site)

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
            export_policy="EXPORT_POLICY",
            import_policy="IMPORT_POLICY",
        )
        models.AddressFamily.objects.create(
            routing_instance=bgp_routing_instance,
            afi_safi=choices.AFISAFIChoices.AFI_IPV6_UNICAST,
            export_policy="EXPORT_POLICY",
            import_policy="IMPORT_POLICY",
        )
        models.AddressFamily.objects.create(
            routing_instance=bgp_routing_instance,
            afi_safi=choices.AFISAFIChoices.AFI_IPV4_MULTICAST,
        )

        cls.create_data = [
            {
                "afi_safi": choices.AFISAFIChoices.AFI_IPV4_FLOWSPEC,
                "routing_instance": bgp_routing_instance.pk,
                "import_policy": "IMPORT_ALL",
                "export_policy": "EXPORT_NONE",
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
            "import_policy": "IMPORT_V4",
            "export_policy": "EXPORT_V4",
        }

    @skip("Not implemented")
    def test_notes_url_on_object(self):
        pass


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
#         # Properties not set on the instance
#         self.assertEqual("", response.data["import_policy"])
#         self.assertEqual("", response.data["export_policy"])
#
#         # Retrieve with inheritance
#         url = self._get_detail_url(instance)
#         response = self.client.get(f"{url}?include_inherited", **self.header)
#         self.assertHttpStatus(response, status.HTTP_200_OK)
#         # Properties not set on the instance but inheritable from the parent address-families
#         self.assertEqual("IMPORT_POLICY", response.data["import_policy"])
#         self.assertEqual("EXPORT_POLICY", response.data["export_policy"])
#
#         # Retrieve with explictly excluded inheritance
#         url = self._get_detail_url(instance)
#         response = self.client.get(f"{url}?include_inherited=false", **self.header)
#         self.assertHttpStatus(response, status.HTTP_200_OK)
#         self.assertEqual("", response.data["import_policy"])
#         self.assertEqual("", response.data["export_policy"])
