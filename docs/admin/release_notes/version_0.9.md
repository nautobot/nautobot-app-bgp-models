# v0.9 Release Notes

## Release Overview

This version introduces `PeerGroupAddressFamily` and `PeerEndpointAddressFamily` data models to provide for more granular configuration modeling.

!!! warning
    This version **removes** the `import_policy`, `export_policy`, and `multipath` attributes from the `PeerGroupTemplate`, `PeerGroup`, and `PeerEndpoint` models, as these are generally address-family-specific configuration attributes and are modeled as such now. No data migration is provided at this time (as there is no way to identify **which** AFI-SAFI any existing policy/multipath configs should be migrated to), and upgrading to this version will therefore necessarily result in data loss if you had previously populated these model fields. Back up your configuration or record this data in some other format before upgrading if appropriate.

## Version 0.9.0

### Added

- [#26](https://github.com/nautobot/nautobot-app-bgp-models/issues/26) - Adds `PeerGroupAddressFamily` and `PeerEndpointAddressFamily` data models.
- [#132](https://github.com/nautobot/nautobot-app-bgp-models/pull/132) - Adds `extra_attributes` support to the `AddressFamily` model.

### Removed

- [#132](https://github.com/nautobot/nautobot-app-bgp-models/pull/132) - Removes `import_policy`, `export_policy`, and `multipath` attributes from `PeerGroupTemplate`, `PeerGroup`, and `PeerEndpoint` models. Use the equivalent fields on `PeerGroupAddressFamily` and `PeerEndpointAddressFamily` instead.

### Dependencies

- [#126](https://github.com/nautobot/nautobot-app-bgp-models/pull/126) - Updated development dependencies `mkdocstrings` and `mkdocstrings-python` to `0.22` and `1.4.0` respectively to address CI failures.

## Version 0.9.1

### Changed

- [#150](https://github.com/nautobot/nautobot-app-bgp-models/pull/150) - Relaxed model validation of PeerEndpoint and PeerGroup to allow simultaneously setting `source_ip` and `source_interface` attributes.
