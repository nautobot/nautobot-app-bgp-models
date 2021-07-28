"""Nested/brief alternate REST API serializers for nautobot_bgp_models models."""

from rest_framework import serializers

from nautobot.core.api import WritableNestedSerializer

from nautobot_bgp_models import models

__all__ = (
    "NestedAutonomousSystemSerializer",
    "NestedPeeringRoleSerializer",
    "NestedPeerGroupSerializer",
    "NestedPeerEndpointSerializer",
    "NestedPeerSessionSerializer",
    "NestedAddressFamilySerializer",
)


class NestedAutonomousSystemSerializer(WritableNestedSerializer):
    """Nested/brief serializer for AutonomousSystem."""

    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:nautobot_bgp_models-api:autonomoussystem-detail")

    class Meta:
        model = models.AutonomousSystem
        fields = ["id", "url", "asn"]


class NestedPeeringRoleSerializer(WritableNestedSerializer):
    """Nested/brief serializer for PeeringRole."""

    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:nautobot_bgp_models-api:peeringrole-detail")

    class Meta:
        model = models.PeeringRole
        fields = ["id", "url", "name", "slug", "color"]


class NestedPeerGroupSerializer(WritableNestedSerializer):
    """Nested/brief serializer for PeerGroup."""

    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:nautobot_bgp_models-api:peergroup-detail")

    class Meta:
        model = models.PeerGroup
        fields = ["id", "url", "device_content_type", "device_object_id", "name", "role", "enabled"]


class NestedPeerEndpointSerializer(WritableNestedSerializer):
    """Nested/brief serializer for PeerEndpoint."""

    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:nautobot_bgp_models-api:peerendpoint-detail")

    class Meta:
        model = models.PeerEndpoint
        fields = ["id", "url", "local_ip", "peer_group", "enabled"]


class NestedPeerSessionSerializer(WritableNestedSerializer):
    """Nested/brief serializer for PeerSession."""

    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:nautobot_bgp_models-api:peersession-detail")

    class Meta:
        model = models.PeerSession
        fields = ["id", "url", "role", "status"]


class NestedAddressFamilySerializer(WritableNestedSerializer):
    """Nested/brief serializer for AddressFamily."""

    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:nautobot_bgp_models-api:addressfamily-detail")

    class Meta:
        model = models.AddressFamily
        fields = ["id", "url", "device_content_type", "device_object_id", "afi_safi", "peer_group", "peer_endpoint"]
