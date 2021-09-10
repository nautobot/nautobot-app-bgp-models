"""Dolt compatibility registration."""

from . import tables

try:
    import dolt
except ImportError:
    DOLT_AVAILABLE = False
else:
    DOLT_AVAILABLE = True


# Only do this if Dolt is available (aka "version control").
if DOLT_AVAILABLE:

    from dolt import register_diff_tables, register_versioned_models

    # Tables used to display diffs
    register_diff_tables(
        {
            "nautobot_bgp_models": {
                "autonomoussystem": tables.AutonomousSystemTable,
                "peeringrole": tables.PeeringRoleTable,
                "peergroup": tables.PeerGroupTable,
                "peerendpoint": tables.PeerEndpointTable,
                "peersession": tables.PeerSessionTable,
                "addressfamily": tables.AddressFamilyTable,
            }
        }
    )

    # Register all models w/ Dolt.
    register_versioned_models({"nautobot_bgp_models": True})
