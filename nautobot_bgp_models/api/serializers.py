"""REST API serializers for nautobot_bgp_models models."""

from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers

from nautobot.core.api import ContentTypeField
from nautobot.extras.api.customfields import CustomFieldModelSerializer
from nautobot.extras.api.serializers import TaggedObjectSerializer, StatusModelSerializerMixin
from nautobot.utilities.api import get_serializer_for_model

from nautobot_bgp_models import models

# We have to do this wildcard import of nested_serializers for the "brief" API parameter to work automatically.
from .nested_serializers import *  # noqa:F401,F403 pylint: disable=wildcard-import,unused-wildcard-import


class AutonomousSystemSerializer(TaggedObjectSerializer, StatusModelSerializerMixin, CustomFieldModelSerializer):
    """REST API serializer for AutonomousSystem records."""

    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:nautobot_bgp_models-api:autonomoussystem-detail")

    class Meta:
        model = models.AutonomousSystem
        fields = ["id", "url", "asn", "description", "status", "tags"]


class PeeringRoleSerializer(CustomFieldModelSerializer):
    """REST API serializer for PeeringRole records."""

    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:nautobot_bgp_models-api:peeringrole-detail")

    class Meta:
        model = models.PeeringRole
        fields = ["id", "url", "name", "slug", "color", "description"]


class AbstractPeeringInfoSerializerMixin:
    """Common mixin for PeerGroupSerializer and PeerEndpointSerializer."""

    class Meta:
        fields = [
            "description",
            "enabled",
            "vrf",
            "update_source_content_type",
            "update_source_object_id",
            "update_source",
            "router_id",
            "autonomous_system",
            "maximum_paths_ibgp",
            "maximum_paths_ebgp",
            "maximum_paths_eibgp",
            "maximum_prefix",
            "bfd_multiplier",
            "bfd_minimum_interval",
            "bfd_fast_detection",
            "enforce_first_as",
            "send_community_ebgp",
        ]

    @swagger_serializer_method(serializer_or_field=serializers.DictField)
    def get_update_source(self, obj):
        """Serializer method for 'update_source' GenericForeignKey field."""
        if obj.update_source is None:
            return None
        serializer = get_serializer_for_model(obj.update_source, prefix="Nested")
        context = {"request": self.context["request"]}
        return serializer(obj.update_source, context=context).data


class InheritableFieldsSerializerMixin:
    """Common mixin for Serializers that support an additional `include_inherited` query parameter."""

    def to_representation(self, instance):
        """Render the model instance to a Python dict.

        If `include_inherited` is specified as a request parameter, include inherited field values as appropriate.
        """
        if self.context["request"].query_params.get("include_inherited", "false") != "false":
            inherited_fields = instance.get_fields(include_inherited=True)
            for field, data in inherited_fields.items():
                setattr(instance, field, data["value"])
        return super().to_representation(instance)


class PeerGroupSerializer(
    AbstractPeeringInfoSerializerMixin,
    InheritableFieldsSerializerMixin,
    CustomFieldModelSerializer,
):
    """REST API serializer for PeerGroup records."""

    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:nautobot_bgp_models-api:peergroup-detail")

    # device_content_type = ContentTypeField(
    #     queryset=ContentType.objects.filter(
    #         Q(Q(app_label="dcim", model="device") | Q(app_label="virtualization", model="virtualmachine"))
    #     ),
    # )
    # device = serializers.SerializerMethodField(read_only=True)

    update_source_content_type = ContentTypeField(
        queryset=ContentType.objects.filter(
            Q(Q(app_label="dcim", model="interface") | Q(app_label="virtualization", model="vminterface"))
        ),
        required=False,
        allow_null=True,
    )
    update_source = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.PeerGroup
        fields = [
            "id",
            "url",
            # "device_content_type",
            # "device_object_id",
            # "device",
            "name",
            "role",
            *AbstractPeeringInfoSerializerMixin.Meta.fields,
        ]

    # @swagger_serializer_method(serializer_or_field=serializers.DictField)
    # def get_device(self, obj):
    #     """Serializer method for 'device' GenericForeignKey field."""
    #     if obj.device is None:
    #         return None
    #     serializer = get_serializer_for_model(obj.device, prefix="Nested")
    #     context = {"request": self.context["request"]}
    #     return serializer(obj.device, context=context).data


class PeerEndpointSerializer(
    InheritableFieldsSerializerMixin,
    AbstractPeeringInfoSerializerMixin,
    TaggedObjectSerializer,
    CustomFieldModelSerializer,
):
    """REST API serializer for PeerEndpoint records."""

    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:nautobot_bgp_models-api:peerendpoint-detail")

    peer = NestedPeerEndpointSerializer(required=False, allow_null=True)  # noqa: F405
    session = NestedPeerSessionSerializer(required=True, allow_null=True)  # noqa: F405

    update_source_content_type = ContentTypeField(
        queryset=ContentType.objects.filter(
            Q(Q(app_label="dcim", model="interface") | Q(app_label="virtualization", model="vminterface"))
        ),
        required=False,
        allow_null=True,
    )
    update_source = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.PeerEndpoint
        fields = [
            "id",
            "url",
            "local_ip",
            "peer_group",
            "peer",
            "session",
            *AbstractPeeringInfoSerializerMixin.Meta.fields,
            "tags",
        ]

    def create(self, validated_data):
        """Create a new PeerEndpoint and update the peer on both sides."""
        record = super().create(validated_data)
        record.session.update_peers()
        return record

    def update(self, instance, validated_data):
        """When updating an existing PeerEndpoint, ensure peer is properly setup on both side."""
        session_has_been_updated = False
        if instance.session.pk != validated_data.get("session"):
            session_has_been_updated = True

        result = super().update(instance, validated_data)

        if session_has_been_updated:
            result.session.update_peers()

        return result


class PeerSessionSerializer(CustomFieldModelSerializer, StatusModelSerializerMixin):
    """REST API serializer for PeerSession records."""

    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:nautobot_bgp_models-api:peersession-detail")

    endpoints = NestedPeerEndpointSerializer(required=False, many=True)  # noqa: F405

    class Meta:
        model = models.PeerSession
        fields = [
            "id",
            "url",
            "role",
            "authentication_key",
            "status",
            "endpoints",
        ]


class AddressFamilySerializer(InheritableFieldsSerializerMixin, CustomFieldModelSerializer):
    """REST API serializer for AddressFamily records."""

    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:nautobot_bgp_models-api:addressfamily-detail")

    # device_content_type = ContentTypeField(
    #     queryset=ContentType.objects.filter(
    #         Q(Q(app_label="dcim", model="device") | Q(app_label="virtualization", model="virtualmachine"))
    #     ),
    # )
    # device = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.AddressFamily
        fields = [
            "id",
            "url",
            "afi_safi",
            # "device_content_type",
            # "device_object_id",
            # "device",
            "peer_group",
            "peer_endpoint",
            "export_policy",
            "import_policy",
            "redistribute_static_policy",
            "maximum_prefix",
            "multipath",
        ]

    # @swagger_serializer_method(serializer_or_field=serializers.DictField)
    # def get_device(self, obj):
    #     """Serializer method for 'device' GenericForeignKey field."""
    #     if obj.device is None:
    #         return None
    #     serializer = get_serializer_for_model(obj.device, prefix="Nested")
    #     context = {"request": self.context["request"]}
    #     return serializer(obj.device, context=context).data
