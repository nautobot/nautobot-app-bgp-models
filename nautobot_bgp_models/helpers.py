"""BGP helper functions."""


def add_available_asns(instance, asns):
    """Create fake records for all gaps between used Autonomous Systems."""
    new_list = []
    last_asn = None
    for asn_val in asns:
        if asn_val.asn == instance.asn_min:
            new_list.append(asn_val)
            last_asn = asn_val.asn
        elif not last_asn:
            new_list.append({"asn": instance.asn_min, "available": asn_val.asn - instance.asn_min})
            new_list.append(asn_val)
            last_asn = asn_val.asn
        elif instance.asn_min <= asn_val.asn <= instance.asn_max:
            if asn_val.asn - last_asn > 1:
                new_list.append({"asn": last_asn + 1, "available": asn_val.asn - last_asn - 1})
            new_list.append(asn_val)
            last_asn = asn_val.asn
        elif asn_val.asn == instance.asn_max:
            new_list.append(asn_val)
            last_asn = asn_val.asn

    if not asns:
        new_list.append({"asn": instance.asn_min, "available": instance.asn_max - instance.asn_min + 1})
    elif last_asn < instance.asn_max:
        new_list.append({"asn": last_asn + 1, "available": instance.asn_max - last_asn})

    return new_list
