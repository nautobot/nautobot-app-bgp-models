"""Unit tests for nautobot_bgp_models."""

from django.contrib.contenttypes.models import ContentType
from django.test import override_settings

from rest_framework import status

from nautobot.dcim.choices import InterfaceTypeChoices
from nautobot.dcim.models import Device, DeviceRole, DeviceType, Interface, Manufacturer, Site
from nautobot.extras.models import Relationship, RelationshipAssociation, Status
from nautobot.ipam.models import IPAddress, VRF
from nautobot.users.models import ObjectPermission
from nautobot.utilities.testing.api import APIViewTestCases

from nautobot_bgp_models import choices, models


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
    def setUpTestData(cls):
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


class PeeringRoleAPITestCase(APIViewTestCases.APIViewTestCase):
    """Test the PeeringRole API."""

    model = models.PeeringRole
    view_namespace = "plugins-api:nautobot_bgp_models"
    brief_fields = ["color", "display", "id", "name", "slug", "url"]
    create_data = [
        {"name": "Role 1", "slug": "role-1", "color": "ff0000"},
        {"name": "Role 2", "slug": "role-2", "color": "00ff00"},
        {"name": "Role 3", "slug": "role-3", "color": "0000ff", "description": "The third role"},
    ]
    bulk_update_data = {
        "color": "112233",
    }

    @classmethod
    def setUpTestData(cls):
        models.PeeringRole.objects.create(name="Alpha", slug="alpha", color="ff0000")
        models.PeeringRole.objects.create(name="Beta", slug="beta", color="00ff00")
        models.PeeringRole.objects.create(name="Gamma", slug="gamma", color="0000ff")


class PeerGroupAPITestCase(APIViewTestCases.APIViewTestCase):
    """Test the PeerGroup API."""

    model = models.PeerGroup
    view_namespace = "plugins-api:nautobot_bgp_models"
    brief_fields = ["device_content_type", "device_object_id", "display", "enabled", "id", "name", "role", "url"]
    bulk_update_data = {
        "description": "Glenn was here",
        "enabled": True,
        "autonomous_system": None,
    }

    # Nautobot testing doesn't correctly handle the API representation of a Status as a slug instead of a PK yet.
    validation_excluded_fields = ["status"]

    @classmethod
    def setUpTestData(cls):
        status_active = Status.objects.get(slug="active")
        status_active.content_types.add(ContentType.objects.get_for_model(models.AutonomousSystem))

        manufacturer = Manufacturer.objects.create(name="Cisco", slug="cisco")
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model="CSR 1000V", slug="csr1000v")
        site = Site.objects.create(name="Site 1", slug="site-1")
        devicerole = DeviceRole.objects.create(name="Router", slug="router", color="ff0000")
        device = Device.objects.create(
            device_type=devicetype, device_role=devicerole, name="Device 1", site=site, status=status_active
        )
        interface = Interface.objects.create(device=device, name="Loopback1", type=InterfaceTypeChoices.TYPE_VIRTUAL)

        vrf = VRF.objects.create(name="Ark B")
        cls.address = IPAddress.objects.create(
            address="10.1.1.1/24", status=status_active, vrf=vrf, assigned_object=interface
        )

        cls.asn = models.AutonomousSystem.objects.create(asn=4294967294, status=status_active)
        peeringrole = models.PeeringRole.objects.create(name="Internal", slug="internal", color="333333")

        cls.create_data = [
            {
                "name": "Group B",
                "device_content_type": "dcim.device",
                "device_object_id": device.pk,
                "role": peeringrole.pk,
                "description": "Telephone sanitizers",
                "enabled": True,
                "vrf": vrf.pk,
                "update_source_content_type": "dcim.interface",
                "update_source_object_id": interface.pk,
                "router_id": cls.address.pk,
                "autonomous_system": cls.asn.pk,
                "maximum_paths_ibgp": 6,
                "maximum_paths_ebgp": 8,
                "maximum_paths_eibgp": 10,
                "maximum_prefix": 100,
                "bfd_multiplier": 3,
                "bfd_minimum_interval": 100,
                "bfd_fast_detection": True,
                "enforce_first_as": None,
                "send_community_ebgp": False,
            },
            {
                "name": "Group A",
                "device_content_type": "dcim.device",
                "device_object_id": device.pk,
                "role": peeringrole.pk,
            },
            {
                "name": "Group C",
                "device_content_type": "dcim.device",
                "device_object_id": device.pk,
                "role": peeringrole.pk,
                "enabled": False,
            },
        ]

        router_id_relation = Relationship.objects.get(slug="bgp_device_router_id")
        RelationshipAssociation.objects.create(relationship=router_id_relation, source=device, destination=cls.address)

        asn_relation = Relationship.objects.get(slug="bgp_asn")
        RelationshipAssociation.objects.create(relationship=asn_relation, source=cls.asn, destination=device)

        models.PeerGroup.objects.create(name="Group 1", role=peeringrole)
        models.PeerGroup.objects.create(name="Group 2", role=peeringrole)
        models.PeerGroup.objects.create(name="Group 3", role=peeringrole)

        cls.maxDiff = None

    @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
    def test_get_object_include_inherited(self):
        """Test object retrieval with the `include_inherited` flag."""
        instance = self._get_queryset()[0]

        # Add object-level permission
        obj_perm = ObjectPermission(
            name="Test permission",
            constraints={"pk": instance.pk},
            actions=["view"],
        )
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ContentType.objects.get_for_model(self.model))

        # Retrieve without inheritance
        url = self._get_detail_url(instance)
        response = self.client.get(url, **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        # Properties not set on the instance
        self.assertIsNone(response.data["autonomous_system"])
        self.assertIsNone(response.data["router_id"])

        # Retrieve with inheritance
        url = self._get_detail_url(instance)
        response = self.client.get(f"{url}?include_inherited", **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        # Properties not set on the instance but inheritable from the parent device
        self.assertEqual(self.asn.pk, response.data["autonomous_system"])
        self.assertEqual(self.address.pk, response.data["router_id"])

        # Retrieve with explictly excluded inheritance
        url = self._get_detail_url(instance)
        response = self.client.get(f"{url}?include_inherited=false", **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertIsNone(response.data["autonomous_system"])
        self.assertIsNone(response.data["router_id"])


class PeerEndpointAPITestCase(APIViewTestCases.APIViewTestCase):
    """Test the PeerEndpoint API."""

    model = models.PeerEndpoint
    view_namespace = "plugins-api:nautobot_bgp_models"
    brief_fields = [
        "display",
        "enabled",
        "id",
        "local_ip",
        "peer_group",
        "url",
    ]
    bulk_update_data = {
        "enabled": False,
    }

    # Nautobot testing doesn't correctly handle the API representation of a Status as a slug instead of a PK yet.
    validation_excluded_fields = ["status"]

    @classmethod
    def setUpTestData(cls):
        cls.status_active = Status.objects.get(slug="active")
        cls.status_active.content_types.add(ContentType.objects.get_for_model(models.AutonomousSystem))
        cls.status_active.content_types.add(ContentType.objects.get_for_model(models.PeerSession))

        cls.peeringrole = models.PeeringRole.objects.create(name="Internal", slug="internal", color="333333")

        cls.session = (
            models.PeerSession.objects.create(
                role=cls.peeringrole,
                status=cls.status_active,
            ),
            models.PeerSession.objects.create(
                role=cls.peeringrole,
                status=cls.status_active,
            ),
            models.PeerSession.objects.create(
                role=cls.peeringrole,
                status=cls.status_active,
            ),
        )

        manufacturer = Manufacturer.objects.create(name="Cisco", slug="cisco")
        cls.devicetype = DeviceType.objects.create(manufacturer=manufacturer, model="CSR 1000V", slug="csr1000v")
        cls.site = Site.objects.create(name="Site 1", slug="site-1")
        cls.devicerole = DeviceRole.objects.create(name="Router", slug="router", color="ff0000")
        device = Device.objects.create(
            device_type=cls.devicetype,
            device_role=cls.devicerole,
            name="Device 1",
            site=cls.site,
            status=cls.status_active,
        )
        interface = Interface.objects.create(device=device, name="Loopback1", type=InterfaceTypeChoices.TYPE_VIRTUAL)

        cls.vrf = VRF.objects.create(name="Ark B")

        cls.addresses = (
            IPAddress.objects.create(
                address="10.1.1.1/24", status=cls.status_active, assigned_object=interface, vrf=cls.vrf
            ),
            IPAddress.objects.create(
                address="10.1.1.2/24", status=cls.status_active, assigned_object=interface, vrf=cls.vrf
            ),
            IPAddress.objects.create(
                address="10.1.2.2/24", status=cls.status_active, assigned_object=interface, vrf=cls.vrf
            ),
            IPAddress.objects.create(
                address="10.1.2.3/24", status=cls.status_active, assigned_object=interface, vrf=cls.vrf
            ),
            IPAddress.objects.create(
                address="10.1.3.3/24", status=cls.status_active, assigned_object=interface, vrf=cls.vrf
            ),
            IPAddress.objects.create(
                address="10.1.3.4/24", status=cls.status_active, assigned_object=interface, vrf=cls.vrf
            ),
        )

        cls.asn = models.AutonomousSystem.objects.create(asn=4294967294, status=cls.status_active)

        peergroup = models.PeerGroup.objects.create(
            name="Group 1",
            role=cls.peeringrole,
            vrf=cls.vrf,
            router_id=cls.addresses[3],
            autonomous_system=cls.asn,
        )

        models.PeerEndpoint.objects.create(local_ip=cls.addresses[0], peer_group=peergroup, session=cls.session[0])
        models.PeerEndpoint.objects.create(local_ip=cls.addresses[1], peer_group=peergroup, session=cls.session[0])
        models.PeerEndpoint.objects.create(local_ip=cls.addresses[2], peer_group=peergroup, session=cls.session[1])

        cls.create_data = [
            {
                "session": cls.session[1].pk,
                "local_ip": cls.addresses[3].pk,
                "description": "Telephone sanitizers",
                "enabled": True,
                "vrf": cls.vrf.pk,
                "update_source_content_type": "dcim.interface",
                "update_source_object_id": interface.pk,
                "router_id": cls.addresses[3].pk,
                "autonomous_system": cls.asn.pk,
                "maximum_paths_ibgp": 6,
                "maximum_paths_ebgp": 8,
                "maximum_paths_eibgp": 10,
                "maximum_prefix": None,
                "bfd_multiplier": 3,
                "bfd_minimum_interval": 100,
                "bfd_fast_detection": True,
                "enforce_first_as": True,
                "send_community_ebgp": True,
            },
            {"local_ip": cls.addresses[4].pk, "peer_group": peergroup.pk, "session": cls.session[2].pk},
            {"local_ip": cls.addresses[5].pk, "session": cls.session[2].pk},
        ]

        cls.maxDiff = None

    @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
    def test_get_object_include_inherited(self):
        """Test object retrieval with the `include_inherited` flag."""
        instance = self._get_queryset()[0]

        # Add object-level permission
        obj_perm = ObjectPermission(
            name="Test permission",
            constraints={"pk": instance.pk},
            actions=["view"],
        )
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ContentType.objects.get_for_model(self.model))

        # Retrieve without inheritance
        url = self._get_detail_url(instance)
        response = self.client.get(url, **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        # Properties not set on the instance
        self.assertIsNone(response.data["autonomous_system"])
        self.assertIsNone(response.data["router_id"])

        # Retrieve with inheritance
        url = self._get_detail_url(instance)
        response = self.client.get(f"{url}?include_inherited", **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        # Properties not set on the instance but inheritable from the parent peer-group
        self.assertEqual(self.asn.pk, response.data["autonomous_system"])
        self.assertEqual(self.addresses[3].pk, response.data["router_id"])

        # Retrieve with explictly excluded inheritance
        url = self._get_detail_url(instance)
        response = self.client.get(f"{url}?include_inherited=false", **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertIsNone(response.data["autonomous_system"])
        self.assertIsNone(response.data["router_id"])

    def test_invalid_combinations(self):
        """Test various invalid combinations of parameters."""
        obj_perm = ObjectPermission(name="Test permission", actions=["add"])
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ContentType.objects.get_for_model(self.model))

        other_device = Device.objects.create(
            device_type=self.devicetype,
            device_role=self.devicerole,
            name="Device 2",
            site=self.site,
            status=self.status_active,
        )
        other_peergroup = models.PeerGroup.objects.create(name="Group 2", role=self.peeringrole)

        for data, error_key, error_str in (
            (
                # Mismatch between local IP's assigned VRF and the explicitly specified VRF
                {
                    "local_ip": self.addresses[0].pk,
                    "vrf": VRF.objects.create(name="other_vrf").pk,
                    "session": self.session[2].pk,
                },
                "__all__",
                "VRF other_vrf was specified, but one or more attributes refer instead to Ark B",
            ),
            (
                # Mismatch between assigned device and assigned peer-group's device
                {"local_ip": self.addresses[0].pk, "peer_group": other_peergroup.pk, "session": self.session[2].pk},
                "__all__",
                "Various attributes refer to different devices and/or virtual machines",
            ),
        ):
            response = self.client.post(self._get_list_url(), data, format="json", **self.header)
            self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)
            self.assertIn(error_key, response.data)
            self.assertIn(error_str, str(response.data[error_key][0]))

        # TODO: lots more negative test possibilities here...


class PeerSessionAPITestCase(APIViewTestCases.APIViewTestCase):
    """Test the PeerSession API."""

    model = models.PeerSession
    view_namespace = "plugins-api:nautobot_bgp_models"
    brief_fields = ["display", "id", "role", "status", "url"]
    choices_fields = ["status"]

    # Nautobot testing doesn't correctly handle the API representation of a Status as a slug instead of a PK yet.
    # Nautobot testing also doesn't correctly handle the reverse-relation that is "endpoints"
    validation_excluded_fields = ["status", "endpoints"]

    @classmethod
    def setUpTestData(cls):
        status_active = Status.objects.get(slug="active")
        status_active.content_types.add(ContentType.objects.get_for_model(models.PeerSession))

        addresses = (
            IPAddress.objects.create(address="10.1.1.1/24", status=status_active),
            IPAddress.objects.create(address="10.1.1.2/24", status=status_active),
            IPAddress.objects.create(address="10.1.2.2/24", status=status_active),
            IPAddress.objects.create(address="10.1.2.3/24", status=status_active),
            IPAddress.objects.create(address="10.1.3.3/24", status=status_active),
            IPAddress.objects.create(address="10.1.3.4/24", status=status_active),
            IPAddress.objects.create(address="10.1.1.100/24", status=status_active),
        )

        peeringrole_internal = models.PeeringRole.objects.create(name="Internal", slug="internal", color="333333")
        peeringrole_external = models.PeeringRole.objects.create(name="External", slug="external", color="0000ff")

        session_1 = models.PeerSession.objects.create(
            role=peeringrole_internal,
            status=status_active,
        )
        session_2 = models.PeerSession.objects.create(
            role=peeringrole_internal,
            status=status_active,
        )
        session_3 = models.PeerSession.objects.create(
            role=peeringrole_internal,
            status=status_active,
        )
        peerendpoints = (
            models.PeerEndpoint.objects.create(local_ip=addresses[0], session=session_1),
            models.PeerEndpoint.objects.create(local_ip=addresses[1], session=session_1),
            models.PeerEndpoint.objects.create(local_ip=addresses[2], session=session_2),
            models.PeerEndpoint.objects.create(local_ip=addresses[3], session=session_2),
            models.PeerEndpoint.objects.create(local_ip=addresses[4], session=session_3),
            models.PeerEndpoint.objects.create(local_ip=addresses[5], session=session_3),
        )

        peerendpoints[0].peer = peerendpoints[1]
        peerendpoints[1].peer = peerendpoints[0]

        peerendpoints[2].peer = peerendpoints[3]
        peerendpoints[3].peer = peerendpoints[2]

        peerendpoints[4].peer = peerendpoints[5]
        peerendpoints[5].peer = peerendpoints[4]

        cls.create_data = [
            {
                "role": peeringrole_internal.pk,
                "status": "active",
                "authentication_key": "my-secure-BGP-key",
            },
            {
                "role": peeringrole_internal.pk,
                "status": "active",
            },
            {
                "role": peeringrole_internal.pk,
                "status": "active",
            },
        ]

        cls.bulk_update_data = {
            "role": peeringrole_external.pk,
            "authentication_key": "",
        }


class AddressFamilyAPITestCase(APIViewTestCases.APIViewTestCase):
    """Test the AddressFamily API."""

    model = models.AddressFamily
    view_namespace = "plugins-api:nautobot_bgp_models"
    brief_fields = [
        "afi_safi",
        "device_content_type",
        "device_object_id",
        "display",
        "id",
        "peer_endpoint",
        "peer_group",
        "url",
    ]
    choices_fields = ["afi_safi"]

    @classmethod
    def setUpTestData(cls):
        status_active = Status.objects.get(slug="active")
        manufacturer = Manufacturer.objects.create(name="Cisco", slug="cisco")
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model="CSR 1000V", slug="csr1000v")
        site = Site.objects.create(name="Site 1", slug="site-1")
        devicerole = DeviceRole.objects.create(name="Router", slug="router", color="ff0000")
        device = Device.objects.create(device_type=devicetype, device_role=devicerole, name="Device 1", site=site)

        interface_1 = Interface.objects.create(device=device, name="Loopback1", type=InterfaceTypeChoices.TYPE_VIRTUAL)
        interface_2 = Interface.objects.create(device=device, name="Loopback2", type=InterfaceTypeChoices.TYPE_VIRTUAL)

        addresses = (
            IPAddress.objects.create(address="10.1.1.1/24", assigned_object=interface_1, status=status_active),
            IPAddress.objects.create(address="10.1.1.2/24", assigned_object=interface_2, status=status_active),
        )

        peeringrole = models.PeeringRole.objects.create(name="Internal", slug="internal", color="333333")
        peergroup = models.PeerGroup.objects.create(name="Group 1", role=peeringrole)

        peersession = models.PeerSession.objects.create(role=peeringrole, status=status_active)
        peerendpoint_1 = models.PeerEndpoint.objects.create(local_ip=addresses[0], session=peersession)
        peerendpoint_2 = models.PeerEndpoint.objects.create(local_ip=addresses[1], session=peersession)

        models.AddressFamily.objects.create(
            device=device,
            afi_safi=choices.AFISAFIChoices.AFI_IPV4,
            export_policy="EXPORT_POLICY",
            import_policy="IMPORT_POLICY",
        )
        models.AddressFamily.objects.create(
            device=device, afi_safi=choices.AFISAFIChoices.AFI_IPV4, peer_group=peergroup
        )
        models.AddressFamily.objects.create(
            device=device, afi_safi=choices.AFISAFIChoices.AFI_IPV4, peer_endpoint=peerendpoint_1
        )

        cls.create_data = [
            {
                "device_content_type": "dcim.device",
                "device_object_id": device.pk,
                "afi_safi": choices.AFISAFIChoices.AFI_IPV4_FLOWSPEC,
                "peer_group": None,
                "peer_endpoint": None,
                "import_policy": "IMPORT_ALL",
                "export_policy": "EXPORT_NONE",
                "redistribute_static_policy": "REDISTRIBUTE_SOME",
                "maximum_prefix": 100,
                "multipath": True,
            },
            {
                "device_content_type": "dcim.device",
                "device_object_id": device.pk,
                "afi_safi": choices.AFISAFIChoices.AFI_VPNV4,
                "peer_group": peergroup.pk,
                "peer_endpoint": None,
            },
            {
                "device_content_type": "dcim.device",
                "device_object_id": device.pk,
                "afi_safi": choices.AFISAFIChoices.AFI_IPV4,
                "peer_group": None,
                "peer_endpoint": peerendpoint_2.pk,
            },
        ]

        cls.bulk_update_data = {
            "import_policy": "IMPORT_V4",
            "export_policy": "EXPORT_V4",
            "redistribute_static_policy": "REDIST_STATIC_V4",
        }

    @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
    def test_get_object_include_inherited(self):
        """Test object retrieval with the `include_inherited` flag."""
        instance = self._get_queryset().get(peer_endpoint__isnull=False)

        # Add object-level permission
        obj_perm = ObjectPermission(
            name="Test permission",
            constraints={"pk": instance.pk},
            actions=["view"],
        )
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ContentType.objects.get_for_model(self.model))

        # Retrieve without inheritance
        url = self._get_detail_url(instance)
        response = self.client.get(url, **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        # Properties not set on the instance
        self.assertEqual("", response.data["import_policy"])
        self.assertEqual("", response.data["export_policy"])

        # Retrieve with inheritance
        url = self._get_detail_url(instance)
        response = self.client.get(f"{url}?include_inherited", **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        # Properties not set on the instance but inheritable from the parent address-families
        self.assertEqual("IMPORT_POLICY", response.data["import_policy"])
        self.assertEqual("EXPORT_POLICY", response.data["export_policy"])

        # Retrieve with explictly excluded inheritance
        url = self._get_detail_url(instance)
        response = self.client.get(f"{url}?include_inherited=false", **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual("", response.data["import_policy"])
        self.assertEqual("", response.data["export_policy"])
