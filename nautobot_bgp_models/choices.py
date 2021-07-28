"""ChoiceSet definitions for nautobot_bgp_models."""

from nautobot.utilities.choices import ChoiceSet


class AFISAFIChoices(ChoiceSet):
    """Choices for the "afi_safi" field on the AddressFamily model."""

    AFI_IPV4 = "ipv4"
    AFI_IPV4_FLOWSPEC = "ipv4_flowspec"
    AFI_VPNV4 = "vpnv4"
    AFI_IPV6_LU = "ipv6_labeled_unicast"

    CHOICES = (
        (AFI_IPV4, "IPv4"),
        (AFI_IPV4_FLOWSPEC, "IPv4 FlowSpec"),
        (AFI_VPNV4, "VPNv4"),
        (AFI_IPV6_LU, "IPv6 Labeled Unicast"),
    )
