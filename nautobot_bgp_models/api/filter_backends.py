"""Filter Backends in use by BGP models app."""

from nautobot.core.api.filter_backends import NautobotFilterBackend


class IncludeInheritedFilterBackend(NautobotFilterBackend):
    """
    Used by views that work with inheritance (PeerGroupViewSet, PeerEndpointViewSet).

    Recognizes that "include_inherited" is not a filterset parameter but rather a view parameter (see InheritableFieldsViewSetMixin)
    """

    def get_filterset_kwargs(self, request, queryset, view):
        """Pop include_inherited as it is not a valid filter field."""
        kwargs = super().get_filterset_kwargs(request, queryset, view)
        try:
            kwargs["data"].pop("include_inherited")
        except KeyError:
            pass
        return kwargs
