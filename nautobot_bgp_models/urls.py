"""Django urlpatterns declaration for nautobot_bgp_models plugin."""
from django.urls import path

from nautobot.core.views.routers import NautobotUIViewSetRouter
from nautobot.extras.views import ObjectChangeLogView

from . import models, views

router = NautobotUIViewSetRouter()
router.register("autonomous-systems", views.AutonomousSystemUIViewSet)
router.register("routing-instances", views.BGPRoutingInstanceUIViewSet)
router.register("peering-roles", views.PeeringRoleUIViewSet)
router.register("peering-groups", views.PeerGroupUIViewSet)
router.register("peering-group-templates", views.PeerGroupTemplateUIViewSet)
router.register("peer-endpoints", views.PeerEndpointUIViewSet)
router.register("peerings", views.PeeringUIViewSet)
router.register("address-families", views.AddressFamilyUIViewSet)

urlpatterns = [
    path(
        "autonomous-systems/<uuid:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="autonomoussystem_changelog",
        kwargs={"model": models.AutonomousSystem},
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
    path(
        "peer-groups/<uuid:pk>/extra-attributes/",
        views.BgpExtraAttributesView.as_view(),
        name="peergroup_extraattributes",
        kwargs={"model": models.PeerGroup},
    ),
    path(
        "peer-group-templates/<uuid:pk>/extra-attributes/",
        views.BgpExtraAttributesView.as_view(),
        name="peergrouptemplate_extraattributes",
        kwargs={"model": models.PeerGroupTemplate},
    ),
    path(
        "peer-endpoints/<uuid:pk>/extra-attributes/",
        views.BgpExtraAttributesView.as_view(),
        name="peerendpoint_extraattributes",
        kwargs={"model": models.PeerEndpoint},
    ),
]
urlpatterns += router.urls
