"""BGP models utilities."""

import re

from nautobot.utilities.forms import parse_numeric_range


AS_EXPANSION_REGEX = r"\[((?:[0-9]+[?:,-])+[0-9]+)\]"


def expand_as_pattern(value):
    """Expand an AS pattern into a list of ASNs."""
    lead, pattern, remnant = re.split(AS_EXPANSION_REGEX, value, maxsplit=1)
    parsed_range = parse_numeric_range(pattern, base=10)
    for i in parsed_range:
        if re.search(AS_EXPANSION_REGEX, remnant):
            for string2 in expand_as_pattern(remnant):
                yield "".join([lead, format(i, "d"), string2])
        else:
            yield "".join([lead, format(i, "d"), remnant])
