"""REST API URL registration for nautobot_bgp_models."""

from nautobot.core.api import OrderedDefaultRouter

from . import views

# Use instead of rest_framework.routers.DefaultRouter so that we get bulk-update/bulk-delete features
router = OrderedDefaultRouter()

router.register("autonomous-systems", views.AutonomousSystemViewSet)
router.register("peering-roles", views.PeeringRoleViewSet)
router.register("peer-groups", views.PeerGroupViewSet)
router.register("peer-endpoints", views.PeerEndpointViewSet)
router.register("sessions", views.PeerSessionViewSet)
router.register("address-families", views.AddressFamilyViewSet)

urlpatterns = router.urls
