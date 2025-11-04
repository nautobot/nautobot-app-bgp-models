"""Nautobot UI navigation elements for nautobot_bgp_models."""

from nautobot.apps.ui import (
    NavigationIconChoices,
    NavigationWeightChoices,
    NavMenuGroup,
    NavMenuItem,
    NavMenuTab,
)

menu_items = (
    NavMenuTab(
        name="Routing",
        icon=NavigationIconChoices.ROUTING,
        weight=NavigationWeightChoices.ROUTING,
        groups=(
            NavMenuGroup(
                name="BGP - Global",
                weight=100,
                items=(
                    NavMenuItem(
                        link="plugins:nautobot_bgp_models:autonomoussystem_list",
                        name="Autonomous Systems",
                        weight=100,
                        permissions=["nautobot_bgp_models.view_autonomoussystem"],
                    ),
                    NavMenuItem(
                        link="plugins:nautobot_bgp_models:autonomoussystemrange_list",
                        name="Autonomous System Ranges",
                        weight=200,
                        permissions=["nautobot_bgp_models.view_autonomoussystemrange"],
                    ),
                    NavMenuItem(
                        link="plugins:nautobot_bgp_models:peergrouptemplate_list",
                        name="Peer Group Templates",
                        weight=300,
                        permissions=["nautobot_bgp_models.view_peergrouptemplate"],
                    ),
                ),
            ),
            NavMenuGroup(
                name="BGP - Instances",
                weight=200,
                items=(
                    NavMenuItem(
                        link="plugins:nautobot_bgp_models:bgproutinginstance_list",
                        name="Routing Instances",
                        weight=100,
                        permissions=["nautobot_bgp_models.view_bgproutinginstance"],
                    ),
                    NavMenuItem(
                        link="plugins:nautobot_bgp_models:addressfamily_list",
                        name="Address-Families (AFI-SAFI)",
                        weight=200,
                        permissions=["nautobot_bgp_models.view_addressfamily"],
                    ),
                    NavMenuItem(
                        link="plugins:nautobot_bgp_models:peergroup_list",
                        name="Peer Groups",
                        weight=300,
                        permissions=["nautobot_bgp_models.view_peergroup"],
                    ),
                    NavMenuItem(
                        link="plugins:nautobot_bgp_models:peergroupaddressfamily_list",
                        name="Peer Group Address-Families (AFI-SAFI)",
                        weight=400,
                        permissions=["nautobot_bgp_models.view_peergroupaddressfamily"],
                    ),
                ),
            ),
            NavMenuGroup(
                name="BGP - Peerings",
                weight=300,
                items=(
                    NavMenuItem(
                        link="plugins:nautobot_bgp_models:peering_list",
                        name="Peerings",
                        weight=100,
                        permissions=["nautobot_bgp_models.view_peering"],
                    ),
                    NavMenuItem(
                        link="plugins:nautobot_bgp_models:peerendpointaddressfamily_list",
                        name="Peer Endpoint Address-Families (AFI-SAFI)",
                        weight=200,
                        permissions=["nautobot_bgp_models.view_peerendpointaddressfamily"],
                    ),
                ),
            ),
        ),
    ),
)
