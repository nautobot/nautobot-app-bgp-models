"""Nautobot UI navigation elements for nautobot_bgp_models."""

from nautobot.core.apps import NavMenuAddButton, NavMenuGroup, NavMenuItem, NavMenuTab

menu_items = (
    NavMenuTab(
        name="Routing",
        weight=350,
        groups=(
            NavMenuGroup(
                name="BGP - Global",
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
                        ),
                    ),
                    NavMenuItem(
                        link="plugins:nautobot_bgp_models:peergrouptemplate_list",
                        name="Peer Group Templates",
                        permissions=["nautobot_bgp_models.view_peergrouptemplate"],
                        buttons=(
                            NavMenuAddButton(
                                link="plugins:nautobot_bgp_models:peergrouptemplate_add",
                                permissions=["nautobot_bgp_models.add_peergrouptemplate"],
                            ),
                        ),
                    ),
                ),
            ),
            NavMenuGroup(
                name="BGP - Instances",
                weight=100,
                items=(
                    NavMenuItem(
                        link="plugins:nautobot_bgp_models:bgproutinginstance_list",
                        name="Routing Instances",
                        permissions=["nautobot_bgp_models.view_bgproutinginstance"],
                        buttons=(
                            NavMenuAddButton(
                                link="plugins:nautobot_bgp_models:bgproutinginstance_add",
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
            NavMenuGroup(
                name="BGP - Peerings",
                weight=100,
                items=(
                    NavMenuItem(
                        link="plugins:nautobot_bgp_models:peering_list",
                        name="Peerings",
                        permissions=["nautobot_bgp_models.view_peering"],
                        buttons=(
                            NavMenuAddButton(
                                link="plugins:nautobot_bgp_models:peering_add",
                                permissions=["nautobot_bgp_models.add_peering"],
                            ),
                        ),
                    ),
                ),
            ),
        ),
    ),
)
