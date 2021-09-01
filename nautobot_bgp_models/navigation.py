"""Nautobot UI navigation elements for nautobot_bgp_models."""

from nautobot.extras.plugins import PluginMenuButton, PluginMenuItem
from nautobot.utilities.choices import ButtonColorChoices

menu_items = (
    PluginMenuItem(
        link="plugins:nautobot_bgp_models:autonomoussystem_list",
        link_text="Autonomous Systems",
        # TODO permissions
        buttons=(
            PluginMenuButton(
                "plugins:nautobot_bgp_models:autonomoussystem_add",
                "Add",
                "mdi mdi-plus-thick",
                ButtonColorChoices.GREEN,
                # TODO permissions,
            ),
            PluginMenuButton(
                "plugins:nautobot_bgp_models:autonomoussystem_import",
                "Import",
                "mdi mdi-database-import-outline",
                ButtonColorChoices.BLUE,
                # TODO permissions,
            ),
        ),
    ),
    PluginMenuItem(
        link="plugins:nautobot_bgp_models:peeringrole_list",
        link_text="Peering Roles",
        # TODO permissions
        buttons=(
            PluginMenuButton(
                "plugins:nautobot_bgp_models:peeringrole_add",
                "Add",
                "mdi mdi-plus-thick",
                ButtonColorChoices.GREEN,
                # TODO permissions
            ),
            PluginMenuButton(
                "plugins:nautobot_bgp_models:peeringrole_import",
                "Import",
                "mdi mdi-database-import-outline",
                ButtonColorChoices.BLUE,
                # TODO permissions,
            ),
        ),
    ),
    PluginMenuItem(
        link="plugins:nautobot_bgp_models:peergroup_list",
        link_text="Peer Groups",
        # TODO permissions
        buttons=(
            PluginMenuButton(
                "plugins:nautobot_bgp_models:peergroup_add",
                "Add",
                "mdi mdi-plus-thick",
                ButtonColorChoices.GREEN,
                # TODO permissions
            ),
        ),
    ),
    PluginMenuItem(
        link="plugins:nautobot_bgp_models:peersession_list",
        link_text="Peer Sessions",
        # TODO permissions
        buttons=(
            PluginMenuButton(
                "plugins:nautobot_bgp_models:peersession_add",
                "Add",
                "mdi mdi-plus-thick",
                ButtonColorChoices.GREEN,
                # TODO permissions
            ),
        ),
    ),
    PluginMenuItem(
        link="plugins:nautobot_bgp_models:addressfamily_list",
        link_text="Address-families (AFI-SAFI)",
        # TODO permissions
        buttons=(
            PluginMenuButton(
                "plugins:nautobot_bgp_models:addressfamily_add",
                "Add",
                "mdi mdi-plus-thick",
                ButtonColorChoices.GREEN,
                # TODO permissions
            ),
        ),
    ),
)
