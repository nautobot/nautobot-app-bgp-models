# v2.4 Release Notes

This document describes all new features and changes in the release. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Release Overview

- Changed minimum Nautobot version to 2.4.20.
- Dropped support for Python 3.9.

<!-- towncrier release notes start -->
## [v2.4.0 (2025-12-12)](https://github.com/nautobot/nautobot-app-bgp-models/releases/tag/v2.4.0)

### Fixed

- [#289](https://github.com/nautobot/nautobot-app-bgp-models/issues/289) - Fixed minor UI bugs.

### Dependencies

- [#566](https://github.com/nautobot/nautobot-app-bgp-models/issues/566) - Pinned Django debug toolbar to <6.0.0.

### Housekeeping

- [#268](https://github.com/nautobot/nautobot-app-bgp-models/issues/268) - Migrated views to the UI Component Framework.
- [#269](https://github.com/nautobot/nautobot-app-bgp-models/issues/269) - Added generate_bgp_test_data management command.
- [#270](https://github.com/nautobot/nautobot-app-bgp-models/issues/270) - Changed Nautobot imports to use nautobot.apps.
- Rebaked from the cookie `nautobot-app-v2.5.1`.
- Rebaked from the cookie `nautobot-app-v2.6.0`.
- Rebaked from the cookie `nautobot-app-v2.7.0`.
- Rebaked from the cookie `nautobot-app-v2.7.1`.
- Rebaked from the cookie `nautobot-app-v2.7.2`.
