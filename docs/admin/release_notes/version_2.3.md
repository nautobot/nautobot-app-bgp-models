
# v2.3 Release Notes

This document describes all new features and changes in the release. The format is based on [Keep a
Changelog](https://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic
Versioning](https://semver.org/spec/v2.0.0.html).

## Release Overview

- Python 3.12 Support

## [v2.3.0 (2024-12-02)](https://github.com/nautobot/nautobot-app-bgp-models/releases/tag/v2.3.0)

### Added

- [#221](https://github.com/nautobot/nautobot-app-bgp-models/issues/221) - Added support for Python 3.12.

### Housekeeping

- Rebaked from the cookie `nautobot-app-v2.4.0`.
- [#199](https://github.com/nautobot/nautobot-app-bgp-models/issues/199) - Updated the documentation to be in sync with the latest default configuration.
- [#219](https://github.com/nautobot/nautobot-app-bgp-models/issues/219) - Rebaked from the cookie `nautobot-app-v2.3.0`.
- [#221](https://github.com/nautobot/nautobot-app-bgp-models/issues/221) - Rebaked from the cookie `nautobot-app-v2.3.2`.
- [#225](https://github.com/nautobot/nautobot-app-bgp-models/issues/225) - Changed model_class_name in .cookiecutter.json to a valid model to help with drift management.

## [v2.3.1 (2025-03-13)](https://github.com/nautobot/nautobot-app-bgp-models/releases/tag/v2.3.1)

### Added in v2.3.1

- [#226](https://github.com/nautobot/nautobot-app-bgp-models/issues/226) - Added `q` search filters to `AddressFamilyFilterSet` and `PeeringFilterSet`.

### Changed in v2.3.1

- [#192](https://github.com/nautobot/nautobot-app-bgp-models/issues/192) - Changed all `q` search methods to use `SearchFilter`.

### Fixed in v2.3.1

- [#232](https://github.com/nautobot/nautobot-app-bgp-models/issues/232) - Fixed PeerEndpoint validation to allow all interfaces (including Virtual Chassis)

### Housekeeping in v2.3.1
- Rebaked from the cookie `nautobot-app-v2.4.2`.
- Rebaked from the cookie `nautobot-app-v2.4.1`.
