"""Django urlpatterns declaration for nautobot_bgp_models app."""

from django.templatetags.static import static
from django.urls import path
from django.views.generic import RedirectView
from nautobot.core.views.routers import NautobotUIViewSetRouter

from . import models, views

router = NautobotUIViewSetRouter()
router.register("autonomous-systems", views.AutonomousSystemUIViewSet)
router.register("autonomous-system-ranges", views.AutonomousSystemRangeUIViewSet)
router.register("routing-instances", views.BGPRoutingInstanceUIViewSet)
router.register("peer-groups", views.PeerGroupUIViewSet)
router.register("peer-group-templates", views.PeerGroupTemplateUIViewSet)
router.register("peer-endpoints", views.PeerEndpointUIViewSet)
router.register("peerings", views.PeeringUIViewSet)
router.register("address-families", views.AddressFamilyUIViewSet)
router.register("peer-group-address-families", views.PeerGroupAddressFamilyUIViewSet)
router.register("peer-endpoint-address-families", views.PeerEndpointAddressFamilyUIViewSet)

urlpatterns = [
    # Extra Attribute views.
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
    path(
        "address-families/<uuid:pk>/extra-attributes/",
        views.BgpExtraAttributesView.as_view(),
        name="addressfamily_extraattributes",
        kwargs={"model": models.AddressFamily},
    ),
    path(
        "peer-group-address-families/<uuid:pk>/extra-attributes/",
        views.BgpExtraAttributesView.as_view(),
        name="peergroupaddressfamily_extraattributes",
        kwargs={"model": models.PeerGroupAddressFamily},
    ),
    path(
        "peer-endpoint-address-families/<uuid:pk>/extra-attributes/",
        views.BgpExtraAttributesView.as_view(),
        name="peerendpointaddressfamily_extraattributes",
        kwargs={"model": models.PeerEndpointAddressFamily},
    ),
    path("peerings/add/", views.PeeringAddView.as_view(), name="peering_add"),
    path("docs/", RedirectView.as_view(url=static("nautobot_bgp_models/docs/index.html")), name="docs"),
]
urlpatterns += router.urls
