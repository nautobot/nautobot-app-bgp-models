# v3.1 Release Notes

This document describes all new features and changes in the release. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Release Overview

This release adds support for Python 3.14.

<!-- towncrier release notes start -->

## [v3.1.2 (2026-09-21)](https://github.com/nautobot/nautobot-app-bgp-models/releases/tag/v3.1.2)

### Added

- [#312](https://github.com/nautobot/nautobot-app-bgp-models/issues/312) - Added new various new AFI-SAFI address family choices.
- [#328](https://github.com/nautobot/nautobot-app-bgp-models/issues/328) - Added a `device` filter to the Autonomous System and Address Family list views and REST API endpoints.

### Fixed

- [#328](https://github.com/nautobot/nautobot-app-bgp-models/issues/328) - Fixed the Autonomous Systems, Address Families, and BGP Peerings panels on the Device detail view linking to list views filtered by `routing_instance__device`, which is not a valid filter on those list views.

### Housekeeping

- Rebaked from the cookie `nautobot-app-v3.1.4`.

## [v3.1.1 (2026-04-10)](https://github.com/nautobot/nautobot-app-bgp-models/releases/tag/v3.1.1)

### Housekeeping

- Rebaked from the cookie `nautobot-app-v3.1.3`.

## [v3.1.0 (2026-03-17)](https://github.com/nautobot/nautobot-app-bgp-models/releases/tag/v3.1.0)

### Added

- Added support for Python 3.14.

### Housekeeping

- Rebaked from the cookie `nautobot-app-v3.1.1`.
