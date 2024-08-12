# BGP Data Models

This app adds the following data models to Nautobot:

- AutonomousSystem
- AutonomousSystemRange
- PeeringRole
- BGPRoutingInstance
- AddressFamily
- PeerGroupTemplate
- PeerGroup
- PeerGroupAddressFamily
- PeerEndpoint
- PeerEndpointAddressFamily
- Peering

A key motivation behind this design is the idea that the Source of Truth should take a network-wide view of the BGP configuration rather than a per-device view. This especially applies to the data models for autonomous systems (ASNs), BGP peerings, and network-wide templates (Peer Groups).

The data models introduced by the BGP app support the following Nautobot features:

- Rest API
- GraphQL
- Custom fields
- Custom Links
- Relationships
- Change logging
- Custom data validation logic
- Webhooks

!!! note
    The data models defined in this app were inspired by the [Openconfig BGP data model](https://yangcatalog.org/api/services/tree/openconfig-bgp@2021-06-16.yang) and [RFC 9234](https://datatracker.ietf.org/doc/rfc9234/).

### AutonomousSystem

This model represents a network-wide description of a BGP autonomous system (AS). It has fields including the actual AS number (ASN), a description field, foreign key (FK) to a Nautobot `Provider` object, and a FK to a Nautobot `Status` object.

### AutonomousSystemRange

This model represents a range of Autonomous Systems. It describes the range using `name`, minimum ASN number (`asn_min`) and maximum ASN number (`asn_max`) properties, allowing to specify optional foreign key to `Tenant`. 

### PeeringRole

This model operates similarly to Nautobot’s `Status` and `Tag` models, in that instances of this model describe various valid values for the `Role` field used by `PeerGroup` and `Peering` records. Similar to those models, this model has fields including a unique name, unique slug, and HTML color code.

### BGPRoutingInstance

This model represents a device specific BGP process. It has a mandatory FK to a Nautobot `Device`, mandatory FK to a `AutonomousSystem` and following fields:

- Router ID (optional, FK to Nautobot `IPAddress`)
- Description (optional, string)
- Extra Attributes (optional, JSON)

### Extra Attributes

Additional BGP object attributes can be defined in "Extra Attributes" field. Extra attributes are JSON type fields meant to store data defined by the user.

Extra attributes follow the inheritance pattern, thus allowing for the merging of the inherited extra attributes.

Example of the extra attributes:

```json
{"ttl-security": 1, "timers": [6, 20] }
```

Extra Attributes are available for following models:

- `BGPRoutingInstance`
- `AddressFamily`
- `PeerGroupTemplate`
- `PeerGroup`
- `PeerGroupAddressFamily`
- `PeerEndpoint`
- `PeerEndpointAddressFamily`

### AddressFamily

This model represents configuration of a BGP address-family (AFI-SAFI). AddressFamily aims to represent a device specific Address Family instance.

It has a locally unique AFI (address family identifier) field, optional VRF field (FK to Nautobot `VRF`) and following fields:

- Import Policy (optional, string)
- Export Policy (optional, string)

(*) The network-wide modeling of AddressFamilies will be implemented in the future with `AddressFamilyTemplate` model similar to the `PeerGroupTemplate`.

### PeerGroupTemplate

This model represents a network-wide configuration for `PeerGroups`. `PeerGroupTemplate` aims to represent a global configuration, and it has a mandatory `Name` field, and the following fields:

- ASN (optional, FK to `AutonomousSystem`)
- Role (optional, FK to `PeeringRole`)
- Description (string)
- Enabled (bool)
- Secret (optional, FK to Nautobot `Secret`)
- Extra Attributes (optional, JSON)

### PeerGroup

This model represents a common configuration for a group of functionally related BGP peers. Peer Group aims to represent device-specific configuration shared across multiple peerings, and it has a mandatory `Name` field, optional FK to a network-wide `PeerGroupTemplate`, and additional fields including

- ASN (optional, FK to `AutonomousSystem`)
- Source IP (optional, FK to Nautobot `IPAddress`, mutually-exclusive with Source Interface)
- Source Interface (optional, FK to Nautobot `Interface`, mutually-exclusive with Source IP)
- Role (optional, FK to `PeeringRole`)
- Description (string)
- Enabled (bool)
- Secret (optional, FK to Nautobot `Secret`)
- Extra Attributes (optional, JSON)

### PeerGroupAddressFamily

This model represents address-family-specific configuration of a PeerGroup. It has a mandatory FK to a `PeerGroup` and a mandatory `afi_safi` field, and additional fields including

- Import Policy (optional, string)
- Export Policy (optional, string)
- Extra Attributes (optional, JSON)

### PeerEndpoint

PeerEndpoint records are created when the Peering instance is created.

This model represents the configuration of a single device for a single BGP peering.

Note that in the case of an external peering (connection with an ISP or Transit Provider), there is no need to create and model the provider's `Device` object. However, as a minimum `PeerEndpoint` (representing the provider's side of `Peering`) created during `Peering` object creation, will have to store IP Address and ASN.

`PeerEndpoint` model has a mandatory FK to a BGP Routing Instance (`BGPRoutingInstance`) record, an optional foreign-key relationship to a `PeerGroup`, and additional keys including:

- ASN (optional, FK to `AutonomousSystem`)
- Peer (optional, FK to `PeerEndpoint`)
- Source IP (optional, FK to Nautobot `IPAddress`, mutually-exclusive with Source Interface)
- Source Interface (optional, FK to Nautobot `Interface`, mutually-exclusive with Source IP)
- Role (optional, FK to `PeeringRole`)
- Description (string)
- Enabled (bool)
- Secret (optional, FK to Nautobot `Secret`)
- Extra Attributes (optional, JSON)

#### PeerEndpoint Local-IP

To ease the data presentation and consumption, `PeerEndpoint` provides a property named `local_ip`.

The value of this property will be presented in the app's Graphical User Interface (GUI) and can be used to render configuration templates.

As Source-IP and Source-Interface could be defined at multiple inheritance levels, each Peer Endpoint will have a `local_ip` determined based on the following order:

1. `PeerEndpoint`'s `source_ip` attribute (if exists)
2. `PeerGroup`'s `source_ip` attribute (if exists)
3. `PeerEndpoint`'s `source_interface` attribute (if exists)
4. `PeerGroup`'s `source_interface` attribute (if exists)

### PeerEndpointAddressFamily

This model represents address-family-specific configuration of a device's PeerEndpoint. It has a mandatory FK to a `PeerEndpoint` and a mandatory `afi_safi` field, and additional keys including:

- Import Policy (optional, string)
- Export Policy (optional, string)
- Extra Attributes (optional, JSON)

### Peering

This model represents the shared configuration of a single BGP peer relationship between two endpoints. It has FKs to two `PeerEndpoint` records (representing the two devices involved in the peering), and additional fields including:

- Status (FK to Nautobot `Status`)

!!! note
    The classification of a session as BGP "internal" or "external" is useful in the construction of queries and filters but does not need to be stored as an actual database attribute (as it is implied by whether the ASNs of the two BGPPeerEndpoints involved are identical or different). It is implemented as a derived property of the `Peering` model.

### Inheritance between models

Some models can inherit attribute values, similar to what BGP supports with Peer Group. The inheritance is built hierarchically. The final attribute value will be taken from the first object in the hierarchy, moving from the top, which has given the attribute value defined.

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

As an example, a `PeerEndpoint` associated with a `PeerGroup` will automatically inherit the above attributes of the `PeerGroup` that haven't been defined at the `PeerEndpoint` level. If an attribute is defined at both levels, the value defined in the `PeerEndpoint` will be used.

The inherited values will be automatically displayed in the UI and can be retrieved from the REST API by adding `?include_inherited=true` parameter.

!!! warning
    **BGP models Custom Fields and GraphQL currently does not offer support for BGP Field Inheritance.** See [GraphQL issue #43](https://github.com/nautobot/nautobot-app-bgp-models/issues/43) for details.

Following is the complete documentation of the field inheritance hierarchy. Models are ordered with the topmost having the highest priority. The first model with an assigned attribute value will be used as an inheritance source.

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

**PeerGroupAddressFamily**:

| **Attribute** | **Inheritance from model** |
| ------------- | -------------------------- |
| extra_attributes | AddressFamily (same `afi_safi` only) |

**PeerEndpointAddressFamily**:

| **Attribute** | **Inheritance from model** |
| ------------- | -------------------------- |
| extra_attributes | PeerGroupAddressFamily (same `afi_safi` only) &rarr; AddressFamily (same `afi_safi` only) |
| import_policy | PeerGroupAddressFamily (same `afi_safi` only) |
| export_policy | PeerGroupAddressFamily (same `afi_safi` only) |
| multipath     | PeerGroupAddressFamily (same `afi_safi` only) |
