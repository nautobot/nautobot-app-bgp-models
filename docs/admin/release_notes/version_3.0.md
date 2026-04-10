# v3.0 Release Notes

This document describes all new features and changes in the release. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Release Overview

This major release marks the compatibility of the BGP Models App with Nautobot 3.0.0. Check out the [full details](https://docs.nautobot.com/projects/core/en/stable/release-notes/version-3.0/) of the changes included in this new major release of Nautobot. Highlights:

- Minimum Nautobot version supported is 3.0.
- Added support for Python 3.13 and removed support for 3.9.
- Updated UI framework to use latest Bootstrap 5.3.

We will continue to support the previous major release for users of Nautobot LTM 2.4 only with critical bug and security fixes as per the [Software Lifecycle Policy](https://networktocode.com/company/legal/software-lifecycle-policy/).

<!-- towncrier release notes start -->

## [v3.0.2 (2026-04-10)](https://github.com/nautobot/nautobot-app-bgp-models/releases/tag/v3.0.2)

### Housekeeping

- Rebaked from the cookie `nautobot-app-v3.1.1`.
- Rebaked from the cookie `nautobot-app-v3.1.3`.

## [v3.0.1 (2026-02-18)](https://github.com/nautobot/nautobot-app-bgp-models/releases/tag/v3.0.1)

### Added

- [#298](https://github.com/nautobot/nautobot-app-bgp-models/issues/298) - Added missing filter definitions to applicable models.
- [#301](https://github.com/nautobot/nautobot-app-bgp-models/issues/301) - Updated PeerEndpoint VRF validation to include related interface as a source for VRF configuration.

### Changed

- [#290](https://github.com/nautobot/nautobot-app-bgp-models/issues/290) - Changed search filter on PeerEndpoint, AddressFamily, and PeerEndpointAddressFamily to perform "contains" filtering on device names instead of "exact" matching.

### Fixed

- [#304](https://github.com/nautobot/nautobot-app-bgp-models/issues/304) - Fixed an issue where Interfaces on a module were not being presented to apply to a BGP Peering or Peer Groups.
- [#304](https://github.com/nautobot/nautobot-app-bgp-models/issues/304) - Fixed an issue where IP Addresses assigned to interfaces on a module were not being presented to apply to a BGP Peering or Peer Groups.

### Documentation

- [#295](https://github.com/nautobot/nautobot-app-bgp-models/issues/295) - Updated documentation to include 3.0 screenshots.

### Housekeeping

- [#290](https://github.com/nautobot/nautobot-app-bgp-models/issues/290) - Updated tests to reflect the new substring based device name filtering.
- [#298](https://github.com/nautobot/nautobot-app-bgp-models/issues/298) - Updated tests to use `FilterTestCase` instead of `BaseFilterTestCase` and `generic_filter_tests` to replace repetitive test cases.
- Rebaked from the cookie `nautobot-app-v3.0.0`.

## [v3.0.0 (2025-11-17)](https://github.com/nautobot/nautobot-app-bgp-models/releases/tag/v3.0.0)

### Added

- Added support for Python 3.13.
- Added support for Nautobot 3.0.

### Changed

- [#280](https://github.com/nautobot/nautobot-app-bgp-models/issues/280) - Updated navigation menu icon and weights to match Nautobot standard.

## [v3.0.0a2 (2025-11-06)](https://github.com/nautobot/nautobot-app-bgp-models/releases/tag/v3.0.0a2)

## [v3.0.0a1 (2025-11-03)](https://github.com/nautobot/nautobot-app-bgp-models/releases/tag/v3.0.0a1)
