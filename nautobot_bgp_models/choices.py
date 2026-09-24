"""ChoiceSet definitions for nautobot_bgp_models."""

from nautobot.apps.choices import ChoiceSet


class AFISAFIChoices(ChoiceSet):
    """Choices for the "afi_safi" field on the AddressFamily model."""

    AFI_IPV4_UNICAST = "ipv4_unicast"
    AFI_IPV4_LABELED_UNICAST = "ipv4_labeled_unicast"
    AFI_IPV4_MULTICAST = "ipv4_multicast"

    AFI_IPV6_UNICAST = "ipv6_unicast"
    AFI_IPV6_LABELED_UNICAST = "ipv6_labeled_unicast"
    AFI_IPV6_MULTICAST = "ipv6_multicast"

    AFI_IPV4_FLOWSPEC = "ipv4_flowspec"
    AFI_IPV6_FLOWSPEC = "ipv6_flowspec"

    AFI_VPNV4_UNICAST = "vpnv4_unicast"
    AFI_VPNV4_MULTICAST = "vpnv4_multicast"
    AFI_VPNV4_FLOWSPEC = "vpnv4_flowspec"

    AFI_VPNV6_UNICAST = "vpnv6_unicast"
    AFI_VPNV6_MULTICAST = "vpnv6_multicast"
    AFI_VPNV6_FLOWSPEC = "vpnv6_flowspec"

    AFI_IPV4_MVPN = "ipv4_mvpn"
    AFI_IPV6_MVPN = "ipv6_mvpn"

    AFI_L2_EVPN = "l2_evpn"
    AFI_L2_VPLS = "l2_vpls"

    AFI_LINKSTATE = "linkstate"
    AFI_LINKSTATE_VPN = "linkstate_vpn"

    AFI_IPV4_SRTE = "ipv4_srte"
    AFI_IPV6_SRTE = "ipv6_srte"

    AFI_IPV4_RT_CONSTRAINT = "ipv4_rt_constraint"

    CHOICES = (
        (AFI_IPV4_UNICAST, "IPv4 Unicast"),
        (AFI_IPV4_LABELED_UNICAST, "IPv4 Labeled Unicast"),
        (AFI_IPV4_MULTICAST, "IPv4 Multicast"),
        (AFI_IPV4_FLOWSPEC, "IPv4 Flowspec"),
        (AFI_IPV4_MVPN, "IPv4 MVPN"),
        (AFI_IPV4_SRTE, "IPv4 SR-TE Policy"),
        (AFI_IPV4_RT_CONSTRAINT, "IPv4 RT Constraint"),
        (AFI_IPV6_UNICAST, "IPv6 Unicast"),
        (AFI_IPV6_LABELED_UNICAST, "IPv6 Labeled Unicast"),
        (AFI_IPV6_MULTICAST, "IPv6 Multicast"),
        (AFI_IPV6_FLOWSPEC, "IPv6 Flowspec"),
        (AFI_IPV6_MVPN, "IPv6 MVPN"),
        (AFI_IPV6_SRTE, "IPv6 SR-TE Policy"),
        (AFI_VPNV4_UNICAST, "VPNv4 Unicast"),
        (AFI_VPNV4_MULTICAST, "VPNv4 Multicast"),
        (AFI_VPNV4_FLOWSPEC, "VPNv4 Flowspec"),
        (AFI_VPNV6_UNICAST, "VPNv6 Unicast"),
        (AFI_VPNV6_MULTICAST, "VPNv6 Multicast"),
        (AFI_VPNV6_FLOWSPEC, "VPNv6 Flowspec"),
        (AFI_L2_EVPN, "L2 EVPN"),
        (AFI_L2_VPLS, "L2 VPLS"),
        (AFI_LINKSTATE, "Link-State"),
        (AFI_LINKSTATE_VPN, "Link-State VPN"),
    )
