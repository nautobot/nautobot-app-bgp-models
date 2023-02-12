"""Nested/brief alternate REST API serializers for nautobot_bgp_models models."""

from rest_framework import serializers

from nautobot.core.api import WritableNestedSerializer

from nautobot_bgp_models import models

__all__ = (
    "NestedAutonomousSystemSerializer",
    "NestedPeerGroupSerializer",
    "NestedPeerGroupTemplateSerializer",
    "NestedPeerEndpointSerializer",
    "NestedPeeringSerializer",
    "NestedAddressFamilySerializer",
    "NestedRoutingInstanceSerializer",
)


class NestedAutonomousSystemSerializer(WritableNestedSerializer):
    """Nested/brief serializer for AutonomousSystem."""

    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:nautobot_bgp_models-api:autonomoussystem-detail")

    class Meta:
        model = models.AutonomousSystem
        fields = ["id", "url", "asn"]


class NestedPeerGroupSerializer(WritableNestedSerializer):
    """Nested/brief serializer for PeerGroup."""

    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:nautobot_bgp_models-api:peergroup-detail")

    class Meta:
        model = models.PeerGroup
        fields = ["id", "url", "name", "role", "enabled"]


class NestedPeerGroupTemplateSerializer(WritableNestedSerializer):
    """Nested/brief serializer for PeerGroup."""

    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:nautobot_bgp_models-api:peergrouptemplate-detail")

    class Meta:
        model = models.PeerGroupTemplate
        fields = ["id", "url", "name", "role", "enabled"]


class NestedPeerEndpointSerializer(WritableNestedSerializer):
    """Nested/brief serializer for PeerEndpoint."""

    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:nautobot_bgp_models-api:peerendpoint-detail")

    class Meta:
        model = models.PeerEndpoint
        fields = ["id", "url"]


class NestedRoutingInstanceSerializer(WritableNestedSerializer):
    """Nested/brief serializer for PeerEndpoint."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:nautobot_bgp_models-api:bgproutinginstance-detail"
    )

    class Meta:
        model = models.BGPRoutingInstance
        fields = ["id", "url"]


class NestedPeeringSerializer(WritableNestedSerializer):
    """Nested/brief serializer for Peering."""

    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:nautobot_bgp_models-api:peering-detail")

    class Meta:
        model = models.Peering
        fields = ["id", "url", "status"]


class NestedAddressFamilySerializer(WritableNestedSerializer):
    """Nested/brief serializer for AddressFamily."""

    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:nautobot_bgp_models-api:addressfamily-detail")

    class Meta:
        model = models.AddressFamily
        fields = ["id", "url", "afi_safi"]
