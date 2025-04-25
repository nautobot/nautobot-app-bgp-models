"""REST API URL registration for nautobot_bgp_models."""

from nautobot.apps.api import OrderedDefaultRouter

from . import views

# Use instead of rest_framework.routers.DefaultRouter so that we get bulk-update/bulk-delete features
router = OrderedDefaultRouter()
# add the name of your api endpoint, usually hyphenated model name in plural, e.g. "my-model-classes"
router.register("autonomous-systems", views.AutonomousSystemViewSet)

app_name = "nautobot_bgp_models-api"
urlpatterns = router.urls
