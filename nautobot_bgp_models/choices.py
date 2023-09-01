"""ChoiceSet definitions for nautobot_bgp_models."""

from nautobot.apps.choices import ChoiceSet


class AFISAFIChoices(ChoiceSet):
    """Choices for the "afi_safi" field on the AddressFamily model."""

    AFI_IPV4_UNICAST = "ipv4_unicast"
    AFI_IPV4_MULTICAST = "ipv4_multicast"

    AFI_IPV6_UNICAST = "ipv6_unicast"
    AFI_IPV6_MULTICAST = "ipv6_multicast"

    AFI_IPV4_FLOWSPEC = "ipv4_flowspec"
    AFI_IPV6_FLOWSPEC = "ipv6_flowspec"

    AFI_VPNV4_UNICAST = "vpnv4_unicast"
    AFI_VPNV4_MULTICAST = "vpnv4_multicast"

    AFI_VPNV6_UNICAST = "vpnv6_unicast"
    AFI_VPNV6_MULTICAST = "vpnv6_multicast"

    AFI_L2_EVPN = "l2_evpn"
    AFI_L2_VPLS = "l2_vpls"

    CHOICES = (
        (AFI_IPV4_UNICAST, "IPv4 Unicast"),
        (AFI_IPV4_MULTICAST, "IPv4 Multicast"),
        (AFI_IPV4_FLOWSPEC, "IPv4 Flowspec"),
        (AFI_IPV6_UNICAST, "IPv6 Unicast"),
        (AFI_IPV6_MULTICAST, "IPv6 Multicast"),
        (AFI_IPV6_FLOWSPEC, "IPv6 Flowspec"),
        (AFI_VPNV4_UNICAST, "VPNv4 Unicast"),
        (AFI_VPNV4_MULTICAST, "VPNv4 Multicast"),
        (AFI_VPNV6_UNICAST, "VPNv6 Unicast"),
        (AFI_VPNV6_MULTICAST, "VPNv6 Multicast"),
        (AFI_L2_EVPN, "L2 EVPN"),
        (AFI_L2_VPLS, "L2 VPLS"),
    )
