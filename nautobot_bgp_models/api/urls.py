"""Django API urlpatterns declaration for nautobot_bgp_models app."""

from nautobot.apps.api import OrderedDefaultRouter

from nautobot_bgp_models.api import views

router = OrderedDefaultRouter()
# add the name of your api endpoint, usually hyphenated model name in plural, e.g. "my-model-classes"
router.register("autonomous-systems", views.AutonomousSystemViewSet)

app_name = "nautobot_bgp_models-api"
urlpatterns = router.urls
