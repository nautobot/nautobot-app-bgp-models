"""REST API serializers for nautobot_bgp_models models."""

from rest_framework import serializers, validators

from nautobot.apps.api import (
    NautobotModelSerializer,
    TaggedModelSerializerMixin,
)
from nautobot.core.settings_funcs import is_truthy

from nautobot_bgp_models import models


class AutonomousSystemSerializer(
    NautobotModelSerializer,
    TaggedModelSerializerMixin,
):
    """REST API serializer for AutonomousSystem records."""

    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:nautobot_bgp_models-api:autonomoussystem-detail")

    class Meta:
        model = models.AutonomousSystem
        fields = "__all__"


class InheritableFieldsSerializerMixin:
    """Common mixin for Serializers that support an additional `include_inherited` query parameter."""

    def to_representation(self, instance):
        """Render the model instance to a Python dict.

        If `include_inherited` is specified as a request parameter, include inherited field values as appropriate.
        """
        req = self.context["request"]
        if hasattr(req, "query_params") and is_truthy(req.query_params.get("include_inherited", False)):
            inherited_fields = instance.get_fields(include_inherited=True)
            for field, data in inherited_fields.items():
                setattr(instance, field, data["value"])
        return super().to_representation(instance)


class ExtraAttributesSerializerMixin(serializers.Serializer):  # pylint: disable=abstract-method
    """Common mixin for BGP Extra Attributes."""

    extra_attributes = serializers.JSONField(required=False, allow_null=True)

    def to_representation(self, instance):
        """Render the model instance to a Python dict.

        If `include_inherited` is specified as a request parameter, include object's get_extra_attributes().
        """
        req = self.context["request"]
        if hasattr(req, "query_params") and is_truthy(req.query_params.get("include_inherited", False)):
            setattr(instance, "extra_attributes", instance.get_extra_attributes())
        return super().to_representation(instance)


class PeerGroupTemplateSerializer(NautobotModelSerializer, ExtraAttributesSerializerMixin):
    """REST API serializer for PeerGroup records."""

    class Meta:
        model = models.PeerGroupTemplate
        fields = "__all__"


class PeerGroupSerializer(
    InheritableFieldsSerializerMixin,
    NautobotModelSerializer,
    ExtraAttributesSerializerMixin,
):
    """REST API serializer for PeerGroup records."""

    class Meta:
        model = models.PeerGroup
        fields = "__all__"
        validators = []

    def validate(self, data):
        """Custom validation logic to handle unique-together with a nullable field."""
        if data.get("vrf"):
            validator = validators.UniqueTogetherValidator(
                queryset=models.PeerGroup.objects.all(), fields=("routing_instance", "name", "vrf")
            )
            validator(data, self)

        super().validate(data)
        return data


class PeerEndpointSerializer(
    InheritableFieldsSerializerMixin,
    TaggedModelSerializerMixin,
    NautobotModelSerializer,
    ExtraAttributesSerializerMixin,
):
    """REST API serializer for PeerEndpoint records."""

    class Meta:
        model = models.PeerEndpoint
        fields = "__all__"

    def create(self, validated_data):
        """Create a new PeerEndpoint and update the peer on both sides."""
        record = super().create(validated_data)
        record.peering.update_peers()
        return record

    def update(self, instance, validated_data):
        """When updating an existing PeerEndpoint, ensure peer is properly setup on both side."""
        peering_has_been_updated = False
        if instance.peering.pk != validated_data.get("peering"):
            peering_has_been_updated = True

        result = super().update(instance, validated_data)

        if peering_has_been_updated:
            result.peering.update_peers()

        return result


class BGPRoutingInstanceSerializer(NautobotModelSerializer, ExtraAttributesSerializerMixin):
    """REST API serializer for Peering records."""

    class Meta:
        model = models.BGPRoutingInstance
        fields = "__all__"


class PeeringSerializer(NautobotModelSerializer):
    """REST API serializer for Peering records."""

    class Meta:
        model = models.Peering
        fields = "__all__"


class AddressFamilySerializer(NautobotModelSerializer, ExtraAttributesSerializerMixin):
    """REST API serializer for AddressFamily records."""

    class Meta:
        model = models.AddressFamily
        fields = "__all__"


class PeerGroupAddressFamilySerializer(NautobotModelSerializer, ExtraAttributesSerializerMixin):
    """REST API serializer for PeerGroupAddressFamily records."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:nautobot_bgp_models-api:peergroupaddressfamily-detail"
    )

    class Meta:
        model = models.PeerGroupAddressFamily
        fields = "__all__"


class PeerEndpointAddressFamilySerializer(NautobotModelSerializer, ExtraAttributesSerializerMixin):
    """REST API serializer for PeerEndpointAddressFamily records."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:nautobot_bgp_models-api:peerendpointaddressfamily-detail"
    )

    class Meta:
        model = models.PeerEndpointAddressFamily
        fields = "__all__"
