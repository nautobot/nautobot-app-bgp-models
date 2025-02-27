"""REST API URL registration for nautobot_bgp_models."""

from nautobot.apps.api import OrderedDefaultRouter

from . import views

# Use instead of rest_framework.routers.DefaultRouter so that we get bulk-update/bulk-delete features
router = OrderedDefaultRouter()

app_name = "nautobot_bgp_models-api"
urlpatterns = router.urls
