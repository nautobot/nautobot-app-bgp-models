"""Nautobot UI navigation elements for nautobot_bgp_models."""

from nautobot.core.apps import NavMenuAddButton, NavMenuGroup, NavMenuItem, NavMenuTab, NavMenuImportButton

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
                            NavMenuImportButton(
                                link="plugins:nautobot_bgp_models:autonomoussystem_import",
                                permissions=["nautobot_bgp_models.add_autonomoussystem"],
                            ),
                        ),
                    ),
                    NavMenuItem(
                        link="plugins:nautobot_bgp_models:autonomoussystemrange_list",
                        name="Autonomous System Ranges",
                        permissions=["nautobot_bgp_models.view_autonomoussystemrange"],
                        buttons=(
                            NavMenuAddButton(
                                link="plugins:nautobot_bgp_models:autonomoussystemrange_add",
                                permissions=["nautobot_bgp_models.add_autonomoussystemrange"],
                            ),
                            NavMenuImportButton(
                                link="plugins:nautobot_bgp_models:autonomoussystemrange_import",
                                permissions=["nautobot_bgp_models.add_autonomoussystemrange"],
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
                            NavMenuImportButton(
                                link="plugins:nautobot_bgp_models:peergrouptemplate_import",
                                permissions=["nautobot_bgp_models.add_peergrouptemplate"],
                            ),
                        ),
                    ),
                    NavMenuItem(
                        link="plugins:nautobot_bgp_models:peergrouptemplateendpoint_list",
                        name="Peer Group Template End Points",
                        permissions=["nautobot_bgp_models.view_peergrouptemplateendpoint"],
                        buttons=(
                            NavMenuAddButton(
                                link="plugins:nautobot_bgp_models:peergrouptemplateendpoint_add",
                                permissions=["nautobot_bgp_models.add_peergrouptemplateendpoint"],
                            ),
                            NavMenuImportButton(
                                link="plugins:nautobot_bgp_models:peergrouptemplateendpoint_import",
                                permissions=["nautobot_bgp_models.add_peergrouptemplateendpoint"],
                            ),
                        ),
                    ),
                    NavMenuItem(
                        link="plugins:nautobot_bgp_models:peergrouptemplateaddressfamily_list",
                        name="Peer Group Template Address-families (AFI-SAFI)",
                        permissions=["nautobot_bgp_models.view_peergrouptemplateaddressfamily"],
                        buttons=(
                            NavMenuAddButton(
                                link="plugins:nautobot_bgp_models:peergrouptemplateaddressfamily_add",
                                permissions=["nautobot_bgp_models.add_peergrouptemplateaddressfamily"],
                            ),
                            NavMenuImportButton(
                                link="plugins:nautobot_bgp_models:peergrouptemplateaddressfamily_import",
                                permissions=["nautobot_bgp_models.add_peergrouptemplateaddressfamily"],
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
                                permissions=["nautobot_bgp_models.add_bgproutinginstance"],
                            ),
                            NavMenuImportButton(
                                link="plugins:nautobot_bgp_models:bgproutinginstance_import",
                                permissions=["nautobot_bgp_models.add_bgproutinginstance"],
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
                            NavMenuImportButton(
                                link="plugins:nautobot_bgp_models:addressfamily_import",
                                permissions=["nautobot_bgp_models.add_addressfamily"],
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
                            NavMenuImportButton(
                                link="plugins:nautobot_bgp_models:peergroup_import",
                                permissions=["nautobot_bgp_models.add_peergroup"],
                            ),
                        ),
                    ),
                    NavMenuItem(
                        link="plugins:nautobot_bgp_models:peergroupaddressfamily_list",
                        name="Peer Group Address-families (AFI-SAFI)",
                        permissions=["nautobot_bgp_models.view_peergroupaddressfamily"],
                        buttons=(
                            NavMenuAddButton(
                                link="plugins:nautobot_bgp_models:peergroupaddressfamily_add",
                                permissions=["nautobot_bgp_models.add_peergroupaddressfamily"],
                            ),
                            NavMenuImportButton(
                                link="plugins:nautobot_bgp_models:peergroupaddressfamily_import",
                                permissions=["nautobot_bgp_models.add_peergroupaddressfamily"],
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
                    NavMenuItem(
                        link="plugins:nautobot_bgp_models:peerendpointaddressfamily_list",
                        name="Peer Endpoint Address-families (AFI-SAFI)",
                        permissions=["nautobot_bgp_models.view_peerendpointaddressfamily"],
                        buttons=(
                            NavMenuAddButton(
                                link="plugins:nautobot_bgp_models:peerendpointaddressfamily_add",
                                permissions=["nautobot_bgp_models.add_peerendpointaddressfamily"],
                            ),
                        ),
                    ),
                ),
            ),
        ),
    ),
)
