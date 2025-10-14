"""Django urlpatterns declaration for nautobot_bgp_models app."""

from django.templatetags.static import static
from django.urls import path
from django.views.generic import RedirectView
from nautobot.core.views.routers import NautobotUIViewSetRouter

from . import views

app_name = "nautobot_bgp_models"
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
    path("peerings/add/", views.PeeringAddView.as_view(), name="peering_add"),
    path("docs/", RedirectView.as_view(url=static("nautobot_bgp_models/docs/index.html")), name="docs"),
]
urlpatterns += router.urls
