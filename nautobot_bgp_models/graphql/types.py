"""GraphQL object type definitions for nautobot_bgp_models."""

import graphene
from graphene_django import DjangoObjectType

from nautobot.dcim.graphql.types import DeviceType, InterfaceType
from nautobot.virtualization.graphql.types import VirtualMachineType, VMInterfaceType

from nautobot_bgp_models import filters, models


class DeviceOrVirtualMachineType(graphene.Union):
    """Union of DeviceType and VirtualMachineType types."""

    class Meta:
        types = (DeviceType, VirtualMachineType)

    @classmethod
    def resolve_type(cls, instance, info):
        """Map to either DeviceType or VirtualMachineType as appropriate."""
        if type(instance).__name__ == "Device":
            return DeviceType
        if type(instance).__name__ == "VirtualMachine":
            return VirtualMachineType
        return None


class InterfaceOrVMInterfaceType(graphene.Union):
    """Union of InterfaceType and VMInterfaceType types."""

    class Meta:
        types = (InterfaceType, VMInterfaceType)

    @classmethod
    def resolve_type(cls, instance, info):
        """Map to either InterfaceType or VMInterfaceType as appropriate."""
        if type(instance).__name__ == "Interface":
            return InterfaceType
        if type(instance).__name__ == "VMInterface":
            return VMInterfaceType
        return None


class PeerGroupType(DjangoObjectType):
    """GraphQL type object for PeerGroup model."""

    update_source = InterfaceOrVMInterfaceType()

    class Meta:
        model = models.PeerGroup
        filterset_class = filters.PeerGroupFilterSet


class PeerEndpointType(DjangoObjectType):
    """GraphQL type object for PeerEndpoint model."""

    device = DeviceOrVirtualMachineType()
    update_source = InterfaceOrVMInterfaceType()

    class Meta:
        model = models.PeerEndpoint
        filterset_class = filters.PeerEndpointFilterSet


graphql_types = [PeerGroupType, PeerEndpointType]
