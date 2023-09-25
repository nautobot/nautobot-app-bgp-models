# v0.9 Release Notes

## Release Overview

This version introduces `PeerGroupAddressFamily` and `PeerEndpointAddressFamily` data models to provide for more granular configuration modeling.

!!! warning
    This version **removes** the `import_policy`, `export_policy`, and `multipath` attributes from the `PeerGroupTemplate`, `PeerGroup`, and `PeerEndpoint` models, as these are generally address-family-specific configuration attributes and are modeled as such now. No data migration is provided at this time (as there is no way to identify **which** AFI-SAFI any existing policy/multipath configs should be migrated to), and upgrading to this version will therefore necessarily result in data loss if you had previously populated these model fields. Back up your configuration or record this data in some other format before upgrading if appropriate.

### Added

- [#26](https://github.com/nautobot/nautobot-plugin-bgp-models/issues/26) - Adds `PeerGroupAddressFamily` and `PeerEndpointAddressFamily` data models.
- [#132](https://github.com/nautobot/nautobot-plugin-bgp-models/pull/132) - Adds `extra_attributes` support to the `AddressFamily` model.

### Removed

- [#132](https://github.com/nautobot/nautobot-plugin-bgp-models/pull/132) - Removes `import_policy`, `export_policy`, and `multipath` attributes from `PeerGroupTemplate`, `PeerGroup`, and `PeerEndpoint` models. Use the equivalent fields on `PeerGroupAddressFamily` and `PeerEndpointAddressFamily` instead.
