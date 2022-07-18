"""Django urlpatterns declaration for nautobot_bgp_models plugin."""
from django.urls import path

from nautobot.extras.views import ObjectChangeLogView

from . import models, views

urlpatterns = [
    path("autonomous-systems/", views.AutonomousSystemListView.as_view(), name="autonomoussystem_list"),
    path("autonomous-systems/add/", views.AutonomousSystemEditView.as_view(), name="autonomoussystem_add"),
    # path("autonomous-systems/import/", views.AutonomousSystemBulkImportView.as_view(), name="autonomoussystem_import"),
    path("autonomous-systems/edit/", views.AutonomousSystemBulkEditView.as_view(), name="autonomoussystem_bulk_edit"),
    path(
        "autonomous-systems/delete/",
        views.AutonomousSystemBulkDeleteView.as_view(),
        name="autonomoussystem_bulk_delete",
    ),
    path("autonomous-systems/<uuid:pk>/", views.AutonomousSystemView.as_view(), name="autonomoussystem"),
    path("autonomous-systems/<uuid:pk>/edit/", views.AutonomousSystemEditView.as_view(), name="autonomoussystem_edit"),
    path(
        "autonomous-systems/<uuid:pk>/delete/",
        views.AutonomousSystemDeleteView.as_view(),
        name="autonomoussystem_delete",
    ),
    path(
        "autonomous-systems/<uuid:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="autonomoussystem_changelog",
        kwargs={"model": models.AutonomousSystem},
    ),
    path("routing-instances/", views.BGPRoutingInstanceListView.as_view(), name="bgproutinginstance_list"),
    path("routing-instances/add/", views.BGPRoutingInstanceEditView.as_view(), name="bgproutinginstance_add"),
    path(
        "routing-instances/edit/", views.BGPRoutingInstanceBulkEditView.as_view(), name="bgproutinginstance_bulk_edit"
    ),
    path(
        "routing-instances/delete/",
        views.BGPRoutingInstanceBulkDeleteView.as_view(),
        name="bgproutinginstance_bulk_delete",
    ),
    path("routing-instances/<uuid:pk>/", views.BGPRoutingInstanceView.as_view(), name="bgproutinginstance"),
    path(
        "routing-instances/<uuid:pk>/edit/", views.BGPRoutingInstanceEditView.as_view(), name="bgproutinginstance_edit"
    ),
    path(
        "routing-instances/<uuid:pk>/delete/",
        views.BGPRoutingInstanceDeleteView.as_view(),
        name="bgproutinginstance_delete",
    ),
    path(
        "routing-instances/<uuid:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="bgproutinginstance_changelog",
        kwargs={"model": models.BGPRoutingInstance},
    ),
    path(
        "routing-instances/<uuid:pk>/extra-attributes/",
        views.BgpExtraAttributesView.as_view(),
        name="bgproutinginstance_extraattributes",
        kwargs={"model": models.BGPRoutingInstance},
    ),
    path("peering-roles/", views.PeeringRoleListView.as_view(), name="peeringrole_list"),
    path("peering-roles/add/", views.PeeringRoleEditView.as_view(), name="peeringrole_add"),
    # path("peering-roles/import/", views.PeeringRoleBulkImportView.as_view(), name="peeringrole_import"),
    path("peering-roles/edit/", views.PeeringRoleBulkEditView.as_view(), name="peeringrole_bulk_edit"),
    path("peering-roles/delete/", views.PeeringRoleBulkDeleteView.as_view(), name="peeringrole_bulk_delete"),
    path("peering-roles/<slug:slug>/", views.PeeringRoleView.as_view(), name="peeringrole"),
    path("peering-roles/<slug:slug>/edit/", views.PeeringRoleEditView.as_view(), name="peeringrole_edit"),
    path("peering-roles/<slug:slug>/delete/", views.PeeringRoleDeleteView.as_view(), name="peeringrole_delete"),
    path(
        "peering-roles/<slug:slug>/changelog/",
        ObjectChangeLogView.as_view(),
        name="peeringrole_changelog",
        kwargs={"model": models.PeeringRole},
    ),
    path("peer-groups/", views.PeerGroupListView.as_view(), name="peergroup_list"),
    path("peer-groups/add/", views.PeerGroupEditView.as_view(), name="peergroup_add"),
    path("peer-group/edit/", views.PeerGroupBulkEditView.as_view(), name="peergroup_bulk_edit"),
    path(
        "peer-group/delete/",
        views.PeerGroupBulkDeleteView.as_view(),
        name="peergroup_bulk_delete",
    ),
    path("peer-groups/<uuid:pk>/", views.PeerGroupView.as_view(), name="peergroup"),
    path("peer-groups/<uuid:pk>/edit/", views.PeerGroupEditView.as_view(), name="peergroup_edit"),
    path("peer-groups/<uuid:pk>/delete/", views.PeerGroupDeleteView.as_view(), name="peergroup_delete"),
    path(
        "peer-groups/<uuid:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="peergroup_changelog",
        kwargs={"model": models.PeerGroup},
    ),
    path(
        "peer-groups/<uuid:pk>/extra-attributes/",
        views.BgpExtraAttributesView.as_view(),
        name="peergroup_extraattributes",
        kwargs={"model": models.PeerGroup},
    ),
    path("peer-group-templates/", views.PeerGroupTemplateListView.as_view(), name="peergrouptemplate_list"),
    path("peer-group-templates/add/", views.PeerGroupTemplateEditView.as_view(), name="peergrouptemplate_add"),
    path(
        "peer-group-templates/edit/", views.PeerGroupTemplateBulkEditView.as_view(), name="peergrouptemplate_bulk_edit"
    ),
    path(
        "peer-group-templates/delete/",
        views.PeerGroupTemplateBulkDeleteView.as_view(),
        name="peergrouptemplate_bulk_delete",
    ),
    path("peer-group-templates/<uuid:pk>/", views.PeerGroupTemplateView.as_view(), name="peergrouptemplate"),
    path(
        "peer-group-templates/<uuid:pk>/edit/", views.PeerGroupTemplateEditView.as_view(), name="peergrouptemplate_edit"
    ),
    path(
        "peer-group-templates/<uuid:pk>/delete/",
        views.PeerGroupTemplateDeleteView.as_view(),
        name="peergrouptemplate_delete",
    ),
    path(
        "peer-group-templates/<uuid:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="peergrouptemplate_changelog",
        kwargs={"model": models.PeerGroupTemplate},
    ),
    path(
        "peer-group-templates/<uuid:pk>/extra-attributes/",
        views.BgpExtraAttributesView.as_view(),
        name="peergrouptemplate_extraattributes",
        kwargs={"model": models.PeerGroupTemplate},
    ),
    path("peer-endpoints/", views.PeerEndpointListView.as_view(), name="peerendpoint_list"),
    path("peer-endpoints/add/", views.PeerEndpointEditView.as_view(), name="peerendpoint_add"),
    path("peer-endpoints/<uuid:pk>/", views.PeerEndpointView.as_view(), name="peerendpoint"),
    path("peer-endpoints/<uuid:pk>/edit/", views.PeerEndpointEditView.as_view(), name="peerendpoint_edit"),
    path("peer-endpoints/<uuid:pk>/delete/", views.PeerEndpointDeleteView.as_view(), name="peerendpoint_delete"),
    path(
        "peer-endpoints/<uuid:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="peerendpoint_changelog",
        kwargs={"model": models.PeerEndpoint},
    ),
    path(
        "peer-endpoints/<uuid:pk>/extra-attributes/",
        views.BgpExtraAttributesView.as_view(),
        name="peerendpoint_extraattributes",
        kwargs={"model": models.PeerEndpoint},
    ),
    path("peerings/", views.PeeringListView.as_view(), name="peering_list"),
    path("peerings/add/", views.PeeringAddView.as_view(), name="peering_add"),
    path("peerings/delete/", views.PeeringBulkDeleteView.as_view(), name="peering_bulk_delete"),
    path("peerings/<uuid:pk>/", views.PeeringView.as_view(), name="peering"),
    path("peerings/<uuid:pk>/edit/", views.PeeringEditView.as_view(), name="peering_edit"),
    path("peerings/<uuid:pk>/delete/", views.PeeringDeleteView.as_view(), name="peering_delete"),
    path(
        "peerings/<uuid:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="peering_changelog",
        kwargs={"model": models.Peering},
    ),
    path(
        "peerings/<uuid:peering>/endpoint/add/",
        views.PeerEndpointEditView.as_view(),
        name="peerendpoint_add",
    ),
    path("address-families/", views.AddressFamilyListView.as_view(), name="addressfamily_list"),
    path("address-families/add/", views.AddressFamilyEditView.as_view(), name="addressfamily_add"),
    path("address-families/edit/", views.AddressFamilyBulkEditView.as_view(), name="addressfamily_bulk_edit"),
    path("address-families/delete/", views.AddressFamilyBulkDeleteView.as_view(), name="addressfamily_bulk_delete"),
    path("address-families/<uuid:pk>/", views.AddressFamilyView.as_view(), name="addressfamily"),
    path("address-families/<uuid:pk>/edit/", views.AddressFamilyEditView.as_view(), name="addressfamily_edit"),
    path("address-families/<uuid:pk>/delete/", views.AddressFamilyDeleteView.as_view(), name="addressfamily_delete"),
    path(
        "address-families/<uuid:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="addressfamily_changelog",
        kwargs={"model": models.AddressFamily},
    ),
]
