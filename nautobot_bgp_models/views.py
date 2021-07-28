"""View classes for nautobot_bgp_models."""

from nautobot.core.views import generic
from nautobot.dcim.models import Device, Interface
from nautobot.virtualization.models import VirtualMachine, VMInterface

from . import filters, forms, models, tables


class AutonomousSystemListView(generic.ObjectListView):
    """List/table view of AutonomousSystem records."""

    queryset = models.AutonomousSystem.objects.all()
    table = tables.AutonomousSystemTable
    filterset = filters.AutonomousSystemFilterSet
    filterset_form = forms.AutonomousSystemFilterForm
    action_buttons = ("add", "import", "export")


class AutonomousSystemView(generic.ObjectView):
    """Detail view of a single AutonomousSystem."""

    queryset = models.AutonomousSystem.objects.all()


class AutonomousSystemEditView(generic.ObjectEditView):
    """Create/edit view for an AutonomousSystem."""

    queryset = models.AutonomousSystem.objects.all()
    model_form = forms.AutonomousSystemForm


class AutonomousSystemDeleteView(generic.ObjectDeleteView):
    """Delete view for an AutonomousSystem."""

    queryset = models.AutonomousSystem.objects.all()


class AutonomousSystemBulkImportView(generic.BulkImportView):
    """Bulk-importing view for multiple AutonomousSystems."""

    queryset = models.AutonomousSystem.objects.all()
    model_form = forms.AutonomousSystemCSVForm
    table = tables.AutonomousSystemTable


class AutonomousSystemBulkEditView(generic.BulkEditView):
    """Bulk-editing view for multiple AutonomousSystems."""

    queryset = models.AutonomousSystem.objects.all()
    filterset = filters.AutonomousSystemFilterSet
    table = tables.AutonomousSystemTable
    form = forms.AutonomousSystemBulkEditForm


class AutonomousSystemBulkDeleteView(generic.BulkDeleteView):
    """Bulk-deleting view for multiple AutonomousSystems."""

    queryset = models.AutonomousSystem.objects.all()
    filterset = filters.AutonomousSystemFilterSet
    table = tables.AutonomousSystemTable


class PeeringRoleListView(generic.ObjectListView):
    """List/table view of PeeringRole records."""

    queryset = models.PeeringRole.objects.all()
    table = tables.PeeringRoleTable
    filterset = filters.PeeringRoleFilterSet
    filterset_form = forms.PeeringRoleFilterForm
    action_buttons = ("add", "import", "export")


class PeeringRoleView(generic.ObjectView):
    """Detail view of a single PeeringRole."""

    queryset = models.PeeringRole.objects.all()


class PeeringRoleEditView(generic.ObjectEditView):
    """Create/edit view for a PeeringRole."""

    queryset = models.PeeringRole.objects.all()
    model_form = forms.PeeringRoleForm


class PeeringRoleDeleteView(generic.ObjectDeleteView):
    """Delete view for a PeeringRole."""

    queryset = models.PeeringRole.objects.all()


class PeeringRoleBulkImportView(generic.BulkImportView):
    """Bulk-importing view for multiple PeeringRoles."""

    queryset = models.PeeringRole.objects.all()
    model_form = forms.PeeringRoleCSVForm
    table = tables.PeeringRoleTable


class PeeringRoleBulkEditView(generic.BulkEditView):
    """Bulk-editing view for multiple PeeringRoles."""

    queryset = models.PeeringRole.objects.all()
    filterset = filters.PeeringRoleFilterSet
    table = tables.PeeringRoleTable
    form = forms.PeeringRoleBulkEditForm


class PeeringRoleBulkDeleteView(generic.BulkDeleteView):
    """Bulk-deleting view for multiple PeeringRoles."""

    queryset = models.PeeringRole.objects.all()
    filterset = filters.PeeringRoleFilterSet
    table = tables.PeeringRoleTable


class PeerGroupListView(generic.ObjectListView):
    """List/table view of PeerGroup records."""

    queryset = models.PeerGroup.objects.all()
    table = tables.PeerGroupTable
    filterset = filters.PeerGroupFilterSet
    filterset_form = forms.PeerGroupFilterForm
    action_buttons = ("add",)


class PeerGroupView(generic.ObjectView):
    """Detail view of a single PeerGroup."""

    queryset = models.PeerGroup.objects.all()

    def get_extra_context(self, request, instance):
        """Return any additional context data for the template."""
        return {"object_fields": instance.get_fields(include_inherited=True)}


class AbstractPeeringInfoEditView(generic.ObjectEditView):
    """Common abstract parent of PeerGroupEditView and PeerEndpointEditView."""

    def alter_obj(self, obj, request, url_args, url_kwargs):
        """Map form fields to object fields."""
        if "device_device" in request.GET:
            try:
                obj.device = Device.objects.get(pk=request.GET["device_device"])
            except (ValueError, Device.DoesNotExist):
                pass
        elif "device_virtualmachine" in request.GET:
            try:
                obj.device = VirtualMachine.objects.get(pk=request.GET["device_virtualmachine"])
            except (ValueError, VirtualMachine.DoesNotExist):
                pass

        if "update_source_interface" in request.GET:
            try:
                obj.update_source = Interface.objects.get(pk=request.GET["update_source_interface"])
            except (ValueError, Interface.DoesNotExist):
                pass
        elif "update_source_vminterface" in request.GET:
            try:
                obj.update_source = VMInterface.objects.get(pk=request.GET["update_source_vminterface"])
            except (ValueError, VMInterface.DoesNotExist):
                pass

        return obj


class PeerGroupEditView(AbstractPeeringInfoEditView):
    """Create/edit view for a PeerGroup."""

    queryset = models.PeerGroup.objects.all()
    model_form = forms.PeerGroupForm
    template_name = "nautobot_bgp_models/peergroup_edit.html"


class PeerGroupDeleteView(generic.ObjectDeleteView):
    """Delete view for a PeerGroup."""

    queryset = models.PeerGroup.objects.all()


class PeerEndpointListView(generic.ObjectListView):
    """List/table view of PeerEndpoint records."""

    queryset = models.PeerEndpoint.objects.all()
    table = tables.PeerEndpointTable
    filterset = filters.PeerEndpointFilterSet
    filterset_form = forms.PeerEndpointFilterForm
    action_buttons = ("add",)


class PeerEndpointView(generic.ObjectView):
    """Detail view of a single PeerEndpoint."""

    queryset = models.PeerEndpoint.objects.all()

    def get_extra_context(self, request, instance):
        """Return any additional context data for the template."""
        return {"object_fields": instance.get_fields(include_inherited=True)}


class PeerEndpointEditView(AbstractPeeringInfoEditView):
    """Create/edit view for a PeerEndpoint."""

    queryset = models.PeerEndpoint.objects.all()
    model_form = forms.PeerEndpointForm
    template_name = "nautobot_bgp_models/peerendpoint_edit.html"


class PeerEndpointDeleteView(generic.ObjectDeleteView):
    """Delete view for a PeerEndpoint."""

    queryset = models.PeerEndpoint.objects.all()


class PeerSessionListView(generic.ObjectListView):
    """List/table view of PeerSession records."""

    queryset = models.PeerSession.objects.all()
    table = tables.PeerSessionTable
    filterset = filters.PeerSessionFilterSet
    filterset_form = forms.PeerSessionFilterForm
    action_buttons = ("add",)


class PeerSessionView(generic.ObjectView):
    """Detail view of a single PeerSession."""

    queryset = models.PeerSession.objects.all()


class PeerSessionEditView(generic.ObjectEditView):
    """Create/edit view for a PeerSession."""

    queryset = models.PeerSession.objects.all()
    model_form = forms.PeerSessionForm


class PeerSessionDeleteView(generic.ObjectDeleteView):
    """Delete view for a PeerSession."""

    queryset = models.PeerSession.objects.all()


class AddressFamilyListView(generic.ObjectListView):
    """List/table view of AddressFamily records."""

    queryset = models.AddressFamily.objects.all()
    table = tables.AddressFamilyTable
    filterset = filters.AddressFamilyFilterSet
    filterset_form = forms.AddressFamilyFilterForm
    action_buttons = ("add",)


class AddressFamilyView(generic.ObjectView):
    """Detail view of a single AddressFamily."""

    queryset = models.AddressFamily.objects.all()

    def get_extra_context(self, request, instance):
        """Return any additional context data for the template."""
        return {"object_fields": instance.get_fields(include_inherited=True)}


class AddressFamilyEditView(generic.ObjectEditView):
    """Create/edit view for an AddressFamily."""

    queryset = models.AddressFamily.objects.all()
    model_form = forms.AddressFamilyForm
    template_name = "nautobot_bgp_models/addressfamily_edit.html"


class AddressFamilyDeleteView(generic.ObjectDeleteView):
    """Delete view for an AddressFamily."""

    queryset = models.AddressFamily.objects.all()
