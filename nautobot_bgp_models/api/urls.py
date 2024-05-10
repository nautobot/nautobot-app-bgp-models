"""REST API URL registration for nautobot_bgp_models."""

from nautobot.apps.api import OrderedDefaultRouter

from . import views

# Use instead of rest_framework.routers.DefaultRouter so that we get bulk-update/bulk-delete features
router = OrderedDefaultRouter()

router.register("autonomous-systems", views.AutonomousSystemViewSet)
router.register("autonomous-system-ranges", views.AutonomousSystemRangeViewSet)
router.register("peer-groups", views.PeerGroupViewSet)
router.register("peer-group-templates", views.PeerGroupTemplateViewSet)
router.register("peer-endpoints", views.PeerEndpointViewSet)
router.register("peerings", views.PeeringViewSet)
router.register("address-families", views.AddressFamilyViewSet)
router.register("peer-group-address-families", views.PeerGroupAddressFamilyViewSet)
router.register("peer-endpoint-address-families", views.PeerEndpointAddressFamilyViewSet)
router.register("routing-instances", views.BGPRoutingInstanceViewSet)

urlpatterns = router.urls
