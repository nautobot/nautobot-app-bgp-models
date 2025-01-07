"""Django urlpatterns declaration for nautobot_bgp_models app."""

from django.templatetags.static import static
from django.urls import path
from django.views.generic import RedirectView
from nautobot.apps.urls import NautobotUIViewSetRouter


from nautobot_bgp_models import views


router = NautobotUIViewSetRouter()

router.register("autonomoussystem", views.AutonomousSystemUIViewSet)


urlpatterns = [
    path("docs/", RedirectView.as_view(url=static("nautobot_bgp_models/docs/index.html")), name="docs"),
]

urlpatterns += router.urls
