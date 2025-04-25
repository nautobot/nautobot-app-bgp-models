"""Django urlpatterns declaration for nautobot_bgp_models app."""

from django.templatetags.static import static
from django.urls import path
from django.views.generic import RedirectView
from nautobot.core.views.routers import NautobotUIViewSetRouter

from . import models, views

app_name = "nautobot_bgp_models"
router = NautobotUIViewSetRouter()

# The standard is for the route to be the hyphenated version of the model class name plural.
# for example, ExampleModel would be example-models.
router.register("autonomous-systems", views.AutonomousSystemUIViewSet)


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
