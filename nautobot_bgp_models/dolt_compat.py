"""Dolt compatibility registration."""

from . import tables

try:
    import dolt  # noqa pylint: disable=unused-import
except ImportError:
    DOLT_AVAILABLE = False
else:
    DOLT_AVAILABLE = True


# Only do this if Dolt is available (aka "version control").
if DOLT_AVAILABLE:
    # Tables used to display diffs
    dolt.register_diff_tables(
        {
            "nautobot_bgp_models": {
                "bgproutinginstance": tables.BGPRoutingInstanceTable,
                "autonomoussystem": tables.AutonomousSystemTable,
                "peergroup": tables.PeerGroupTable,
                "peergroupaddressfamily": tables.PeerGroupAddressFamilyTable,
                "peergrouptemplateaddressfamily": tables.PeerGroupTemplateAddressFamilyTable,
                "peergrouptemplate": tables.PeerGroupTemplateTable,
                "peergrouptemplateendpoint": tables.PeerGroupTemplateEndpointTable,
                "peerendpoint": tables.PeerEndpointTable,
                "peerendpointaddressfamily": tables.PeerEndpointAddressFamilyTable,
                "peering": tables.PeeringTable,
                "addressfamily": tables.AddressFamilyTable,
            }
        }
    )

    # Register all models w/ Dolt.
    dolt.register_versioned_models({"nautobot_bgp_models": True})
