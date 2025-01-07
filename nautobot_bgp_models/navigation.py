"""Menu items."""

from nautobot.apps.ui import NavMenuAddButton, NavMenuGroup, NavMenuItem, NavMenuTab

items = (
    NavMenuItem(
        link="plugins:nautobot_bgp_models:autonomoussystem_list",
        name="BGP Models",
        permissions=["nautobot_bgp_models.view_autonomoussystem"],
        buttons=(
            NavMenuAddButton(
                link="plugins:nautobot_bgp_models:autonomoussystem_add",
                permissions=["nautobot_bgp_models.add_autonomoussystem"],
            ),
        ),
    ),
)

menu_items = (
    NavMenuTab(
        name="Apps",
        groups=(NavMenuGroup(name="BGP Models", items=tuple(items)),),
    ),
)
