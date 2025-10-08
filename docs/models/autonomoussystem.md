# Autonomous System

This model represents a network-wide description of a BGP autonomous system (AS). It has fields including the actual AS number (ASN), a description field, foreign key (FK) to a Nautobot `Provider` object, and a FK to a Nautobot `Status` object.

- `asn` (ASNField): 32-bit autonomous system number.
- `description`: (string): Description for the autonomous system.
- `provider`: (Provider): Provider for the autonomous system.
- `status`: (Status): Status for the autonomous system.
