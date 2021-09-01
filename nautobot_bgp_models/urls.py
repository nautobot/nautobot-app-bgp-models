"""Django urlpatterns declaration for nautobot_bgp_models plugin."""
from django.urls import path

from nautobot.extras.views import ObjectChangeLogView

from . import models, views

urlpatterns = [
    path("autonomous-systems/", views.AutonomousSystemListView.as_view(), name="autonomoussystem_list"),
    path("autonomous-systems/add/", views.AutonomousSystemEditView.as_view(), name="autonomoussystem_add"),
    path("autonomous-systems/import/", views.AutonomousSystemBulkImportView.as_view(), name="autonomoussystem_import"),
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
    path("peering-roles/", views.PeeringRoleListView.as_view(), name="peeringrole_list"),
    path("peering-roles/add/", views.PeeringRoleEditView.as_view(), name="peeringrole_add"),
    path("peering-roles/import/", views.PeeringRoleBulkImportView.as_view(), name="peeringrole_import"),
    path("peering-roles/edit/", views.PeeringRoleBulkEditView.as_view(), name="peeringrole_bulk_edit"),
    path("peering-roles/delete/", views.PeeringRoleBulkDeleteView.as_view(), name="peeringrole_bulk_delete"),
    path("peering-roles/<uuid:pk>/", views.PeeringRoleView.as_view(), name="peeringrole"),
    path("peering-roles/<uuid:pk>/edit/", views.PeeringRoleEditView.as_view(), name="peeringrole_edit"),
    path("peering-roles/<uuid:pk>/delete/", views.PeeringRoleDeleteView.as_view(), name="peeringrole_delete"),
    path(
        "peering-roles/<uuid:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="peeringrole_changelog",
        kwargs={"model": models.PeeringRole},
    ),
    path("peer-groups/", views.PeerGroupListView.as_view(), name="peergroup_list"),
    path("peer-groups/add/", views.PeerGroupEditView.as_view(), name="peergroup_add"),
    path("peer-groups/<uuid:pk>/", views.PeerGroupView.as_view(), name="peergroup"),
    path("peer-groups/<uuid:pk>/edit/", views.PeerGroupEditView.as_view(), name="peergroup_edit"),
    path("peer-groups/<uuid:pk>/delete/", views.PeerGroupDeleteView.as_view(), name="peergroup_delete"),
    path(
        "peer-groups/<uuid:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="peergroup_changelog",
        kwargs={"model": models.PeerGroup},
    ),
    path("peer-endpoints/", views.PeerEndpointListView.as_view(), name="peerendpoint_list"),
    path("peer-endpoints/<uuid:pk>/", views.PeerEndpointView.as_view(), name="peerendpoint"),
    path("peer-endpoints/<uuid:pk>/edit/", views.PeerEndpointEditView.as_view(), name="peerendpoint_edit"),
    path("peer-endpoints/<uuid:pk>/delete/", views.PeerEndpointDeleteView.as_view(), name="peerendpoint_delete"),
    path(
        "peer-endpoints/<uuid:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="peerendpoint_changelog",
        kwargs={"model": models.PeerEndpoint},
    ),
    path("sessions/", views.PeerSessionListView.as_view(), name="peersession_list"),
    path("sessions/add/", views.PeerSessionEditView.as_view(), name="peersession_add"),
    path("sessions/<uuid:pk>/", views.PeerSessionView.as_view(), name="peersession"),
    path("sessions/<uuid:pk>/edit/", views.PeerSessionEditView.as_view(), name="peersession_edit"),
    path("sessions/<uuid:pk>/delete/", views.PeerSessionDeleteView.as_view(), name="peersession_delete"),
    path(
        "sessions/<uuid:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="peersession_changelog",
        kwargs={"model": models.PeerSession},
    ),
    path(
        "sessions/<uuid:session>/endpoint/add/",
        views.PeerEndpointEditView.as_view(),
        name="peerendpoint_add",
    ),
    path("address-families/", views.AddressFamilyListView.as_view(), name="addressfamily_list"),
    path("address-families/add/", views.AddressFamilyEditView.as_view(), name="addressfamily_add"),
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
