"""Nautobot UI navigation elements for nautobot_bgp_models."""

from nautobot.core.apps import NavMenuAddButton, NavMenuImportButton, NavMenuGroup, NavMenuItem, NavMenuTab

menu_items = (
    NavMenuTab(
        name="Routing",
        weight=350,
        groups=(
            NavMenuGroup(
                name="BGP",
                weight=100,
                items=(
                    NavMenuItem(
                        link="plugins:nautobot_bgp_models:autonomoussystem_list",
                        name="Autonomous Systems",
                        permissions=["nautobot_bgp_models.view_autonomoussystem"],
                        buttons=(
                            NavMenuAddButton(
                                link="plugins:nautobot_bgp_models:autonomoussystem_add",
                                permissions=["nautobot_bgp_models.add_autonomoussystem"],
                            ),
                            NavMenuImportButton(
                                link="plugins:nautobot_bgp_models:autonomoussystem_import",
                                permissions=["nautobot_bgp_models.add_autonomoussystem"],
                            ),
                        ),
                    ),
                    NavMenuItem(
                        link="plugins:nautobot_bgp_models:peeringrole_list",
                        name="Peering Roles",
                        permissions=["nautobot_bgp_models.view_peeringrole"],
                        buttons=(
                            NavMenuAddButton(
                                link="plugins:nautobot_bgp_models:peeringrole_add",
                                permissions=["nautobot_bgp_models.add_peeringrole"],
                            ),
                            NavMenuImportButton(
                                link="plugins:nautobot_bgp_models:peeringrole_import",
                                permissions=["nautobot_bgp_models.add_peeringrole"],
                            ),
                        ),
                    ),
                    NavMenuItem(
                        link="plugins:nautobot_bgp_models:peergroup_list",
                        name="Peer Groups",
                        permissions=["nautobot_bgp_models.view_peergroup"],
                        buttons=(
                            NavMenuAddButton(
                                link="plugins:nautobot_bgp_models:peergroup_add",
                                permissions=["nautobot_bgp_models.add_peergroup"],
                            ),
                        ),
                    ),
                    NavMenuItem(
                        link="plugins:nautobot_bgp_models:peersession_list",
                        name="Peer Sessions",
                        permissions=["nautobot_bgp_models.view_peersession"],
                        buttons=(
                            NavMenuAddButton(
                                link="plugins:nautobot_bgp_models:peersession_add",
                                permissions=["nautobot_bgp_models.add_peersession"],
                            ),
                        ),
                    ),
                    NavMenuItem(
                        link="plugins:nautobot_bgp_models:addressfamily_list",
                        name="Address-families (AFI-SAFI)",
                        permissions=["nautobot_bgp_models.view_addressfamily"],
                        buttons=(
                            NavMenuAddButton(
                                link="plugins:nautobot_bgp_models:addressfamily_add",
                                permissions=["nautobot_bgp_models.add_addressfamily"],
                            ),
                        ),
                    ),
                ),
            ),
        ),
    ),
)
