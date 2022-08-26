# Data Models

This plugin adds the following new data models into Nautobot:

- Autonomous System
- Routing Instance
- Peer Endpoint
- Peer Group
- Peer Group Template
- Address Family
- Peering
- Peering Role

A key motivation behind this design is the idea that the Source of Truth should take a network-wide view of the BGP configuration, rather than a device-per-device view. This most directly applies to the data models for autonomous systems (ASNs), BGP peerings and network-wide templates (Peer Groups).

All the data models introduced by the BGP plugin support the following Nautobot features:

- Rest API
- GraphQL
- Custom fields
- Custom Links
- Relationships
- Change logging
- Custom data validation logic
- Webhooks

> The data model defined by this plugin takes inspirations from the Openconfig BGP data model (https://yangcatalog.org/api/services/tree/openconfig-bgp@2021-06-16.yang) and the RFC 9234 (https://datatracker.ietf.org/doc/rfc9234/)

## AutonomousSystem

This model represents a network-wide description of a BGP autonomous system (AS). It has fields including the actual AS number (ASN), a description field, foreign key (FK) to a Nautobot `Provider` object, and a FK to a Nautobot `Status` object.

## BGPRoutingInstance

This model represents a device specific BGP process. It has a mandatory FK to a Nautobot `Device`, mandatory FK to a `AutonomousSystem` and following fields: 

- Router ID (optional, FK to Nautobot `IPAddress`,
- Description (optional, string)
- Extra Attributes (optional, JSON)

## PeerEndpoint

This model represents the configuration of a single device with respect to a single BGP peering. It does not store configuration that must match symmetrically between peer devices (such as a common authentication key). 

Note that in the case of an external peering (device in the locally managed network peering to a remote endpoint belonging to an AS not managed within this network), while there generally will not be a Device record representing the remote endpoint, there will need to be a `PeerEndpoint` record representing it, at a minimum storing the IP address and ASN of the remote endpoint.

`PeerEndpoint` model has a mandatory FK to a BGP Routing Instance (`BGPRoutingInstance`) record, an optional foreign-key relationship to a `PeerGroup`, and additional keys including:

- ASN (optional, FK to `AutonomousSystem`)
- Peer (optional, FK to `PeerEndpoint`)
- Source IP (optional, FK to Nautobot `IPAddress`, mutually-exclusive with Source Interface)
- Source Interface (optional, FK to Nautobot `Interface`, mutually-exclusive with Source IP)
- Role (optional, FK to `PeeringRole`)
- Description (string)
- Enabled (bool)
- Import Policy (optional, string)
- Export Policy (optional, string)
- Secret (optional, FK to Nautobot `Secret`)
- Extra Attributes (optional, JSON)

### PeerEndpoint Local-IP

To ease the data presentation and consumption, `PeerEndpoint` provides also a property named `local_ip`.
The value of this property will be presented in plugin's Grapical User Interface (GUI), and can be used to render configuration templates.

As Source-IP and Source-Interface could be defined at multiple inheritance levels, each Peer Endpoint will have a `local_ip` determined based on the following order:

1. `PeerEndpoint`'s `source_ip` attribute (if exists)
2. `Peer Group`'s `source_ip` attribute (if exists)
3. `PeerEndpoint`'s `source_interface` attribute (if exists)
4. `PeerGroup`'s `source_interface` attribute (if exists)

## PeerGroup

This model represents common configuration for a group of functionally related BGP peers. `PeerGroup` aims to represent device-specific configuration, and it has a mandatory `Name` field, optional FK to a network-wide `PeerGroupTemplate`, and additional fields including:

- ASN (optional, FK to `AutonomousSystem`)
- Source IP (optional, FK to Nautobot `IPAddress`, mutually-exclusive with Source Interface)
- Source Interface (optional, FK to Nautobot `Interface`, mutually-exclusive with Source IP)
- Role (optional, FK to `PeeringRole`)
- Description (string)
- Enabled (bool)
- Import Policy (optional, string)
- Export Policy (optional, string)
- Secret (optional, FK to Nautobot `Secret`)
- Extra Attributes (optional, JSON)

## PeerGroupTemplate

This model represents network-wide configuration for `PeerGroups`. `PeerGroupTemplate` aims to represent a global configuration, and it has a mandatory `Name` field, and following fields:

- ASN (optional, FK to `AutonomousSystem`)
- Role (optional, FK to `PeeringRole`)
- Description (string)
- Enabled (bool)
- Import Policy (optional, string)
- Export Policy (optional, string)
- Secret (optional, FK to Nautobot `Secret`)
- Extra Attributes (optional, JSON)

## Extra Attributes

Additional BGP object's attributes can be modelled by "Extra Attributes". Extra_attributes is a JSON type fields allowing to store data modelled by user.
Extra attributes follow the inheritance pattern, thus allowing for merging the inherited extra attributes.

Examples of the extra attributes might include:

```json
{"ttl-security": 1, "timers": [6, 20] }
```

Extra Attributes are available for following models:

- `PeerEndpoint`
- `PeerGroup`
- `PeerGroupTemplate`
- `BGPRoutingInstance`

## AddressFamily

This model represents configuration of a BGP address-family (AFI-SAFI). AddressFamily aims to represent a device specific Address Family instance.
It has a locally unique AFI (address-family identifier) field, optional VRF field (FK to Nautobot `VRF`) and following fields:

- Import Policy (optional, string)
- Export Policy (optional, string)

(*) The network-wide modelling of AddressFamilies will be implemented in the future with `AddressFamilyTemplate` model similar to the `PeerGroupTemplate`.
The device-specific `PeerEndpoint` custom modeling will be implemented in the future with `PeerEndpointContext` and `PeerGroupContext` models.

## Peering

This model represents the shared configuration of a single BGP peer relationship between two endpoints. It has FKs to two `PeerEndpoint` records (representing the two devices involved in the peering), and additional fields including:

- Status (FK to Nautobot `Status`)

> The nature of a session as BGP “internal” or “external” is useful in the construction of queries and filters, but does not need to be stored as an actual database attribute (as it is implied by whether the ASNs of the two BGPPeerEndpoints involved are identical or different). It is implemented as a derived property of the `Peering` model.

## PeeringRole

This model operates similarly to Nautobot’s `Status` and `Tag` models, in that instances of this model describe various valid values for the `role` field on `PeerGroupTemplate`, `PeerGroup` and/or `PeerEndpoint`. This model has fields including a unique name, unique slug, and a HTML color value.

## Inheritance between models

Some models have a built-in inheritance similar to what BGP supports with PeerGroup. The inheritance can take multi-level lookup between BGP objects, in this case the first found object with the assigned attribute will be considered as an inheritance source.

Example **PeerEndpoint** inheritance details:

- A `PeerEndpoint` inherits `AutonomousSystem` and `extra_attributes` fields from:
  - `PeerGroup`
  - `PeerGroupTemplate`
  - `BGPRoutingInstance`

- A `PeerEndpoint` inherits `description`, `enabled`, `export_policy`, `import_policy` fields from:
  - `PeerGroup`
  - `PeerGroupTemplate`

- A `PeerEndpoint` inherits `source_ip`, `source_interface` fields from:
  - `PeerGroup`

As an example, a `PeerEndpoint` associated with a `PeerGroup` will automatically inherit above attributes of the `PeerGroup` that haven't been defined at the `PeerEndpoint` level. If an attribute is defined on both, the value defined on the `PeerEndpoint` will be used.

The inherited values will be automatically displayed in the UI and can be retrieve from the REST API with the additional `?include_inherited=true` parameter.

(*) **BGP models Custom Fields and GraphQL currently does not offer support for BGP Field Inheritance.** GraphQL issue is tracked under https://github.com/nautobot/nautobot-plugin-bgp-models/issues/43 

Following is the complete documentation of the field inheritance pattern. Models are listed from top priority to the least priority, the first model with an assigned attribute value will be used as an inheritance source.

**PeerEndpoint**:

| **Attribute** | **Inheritance from model**                             |
|---|--------------------------------------------------------|
| autonomous_system | PeerGroup &rarr; PeerGroupTemplate &rarr; BGPRoutingInstance |
| extra_attributes | PeerGroup &rarr; PeerGroupTemplate &rarr; BGPRoutingInstance |
| description | PeerGroup &rarr; PeerGroupTemplate |
| enabled | PeerGroup &rarr; PeerGroupTemplate |
| export_policy | PeerGroup &rarr; PeerGroupTemplate |
| import_policy | PeerGroup &rarr; PeerGroupTemplate |
| role | PeerGroup &rarr; PeerGroupTemplate |
| source_ip | PeerGroup |
| source_interface | PeerGroup |

**PeerGroup**:

| **Attribute** | **Inheritance from model** |
|------|-------------------|
| extra_attributes | PeerGroupTemplate &rarr; BGPRoutingInstance |
| autonomous_system | PeerGroupTemplate |
| description | PeerGroupTemplate |
| enabled | PeerGroupTemplate |
| export_policy | PeerGroupTemplate |
| import_policy | PeerGroupTemplate |
| role | PeerGroupTemplate |
