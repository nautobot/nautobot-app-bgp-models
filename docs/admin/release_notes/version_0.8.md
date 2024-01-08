# v0.8 Release Notes

## Release Overview

- BGP Models v0.8 release

## [v0.8.0] - 2023-08-24

### Added
- [#91](https://github.com/nautobot/nautobot-app-bgp-models/issues/91) - Implements Nautobot Viewsets for UI and API
- [#91](https://github.com/nautobot/nautobot-app-bgp-models/issues/91) - Adds Nautobot Notes support
- [#96](https://github.com/nautobot/nautobot-app-bgp-models/pull/96) - Adds CSV Imports / Exports
- [#97](https://github.com/nautobot/nautobot-app-bgp-models/issues/97) - Adds `Status` field on `BGPRoutingInstance` model
- [#114](https://github.com/nautobot/nautobot-app-bgp-models/pull/114) - Adds `Device Role` and `Peer Endpoint Role` filters on `Peering` model

### Changed
- [#96](https://github.com/nautobot/nautobot-app-bgp-models/pull/96) - Renames field `template` to `peergroup_template` on `PeerGroup` model
- [#116](https://github.com/nautobot/nautobot-app-bgp-models/pull/116) - Disables endpoint ordering in `Peering` table
- [#122](https://github.com/nautobot/nautobot-app-bgp-models/pull/122) - Removes mandatory `Provider` field for external `Peer Endpoints`

### Removed
- [#124](https://github.com/nautobot/nautobot-app-bgp-models/pull/124) - Removes support for Python 3.7
