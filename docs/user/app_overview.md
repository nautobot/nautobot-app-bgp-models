# App Overview

This document provides an overview of the App including critical information and import considerations when applying it to your Nautobot environment.

!!! note
    Throughout this documentation, the terms "app" and "plugin" will be used interchangeably.

## Description

An app for [Nautobot](https://github.com/nautobot/nautobot), extending the core models with BGP-specific models. They enable modeling and management of BGP peerings, whether or not the peer device is present in Nautobot.

This application adds the following new data models into Nautobot:

- **Autonomous System**: network-wide description of a BGP autonomous system (AS)
- **Peering Role**: describes the valid options for PeerGroup, PeerGroupTemplate, and/or Peering roles
- **BGP Routing Instance**: device-specific BGP process
- **Address Family**: device-specific configuration of a BGP address family (AFI-SAFI) with an optional VRF
- **Peer Group Template**: network-wide template for Peer Group objects
- **Peer Group**: device-specific configuration for a group of functionally related BGP peers
- **Peer Group Address Family**: peer-group-specific configuration of a BGP address-family (AFI-SAFI)
- **Peering and Peer Endpoints**: A BGP Peering is represented by a Peering object and two endpoints, each representing the configuration of one side of the BGP peering. A Peer Endpoint must be associated with a BGP Routing Instance.
- **Peer Endpoint Address Family**: peer-specific configuration of a BGP address-family (AFI-SAFI)

With these new models, it's now possible to populate the Source of Truth (SoT) with any BGP peerings, internal or external, regardless of whether both endpoints are fully defined in the Source of Truth.

The minimum requirement to define a BGP peering is two IP addresses and one or two autonomous systems (one ASN for iBGP, two ASNs for eBGP).

## Audience (User Personas) - Who should use this App?

Network Admins who need to model their BGP internal and external peerings inside of their Source of Truth so they can programmatically generate BGP configuration for their devices.

## Authors and Maintainers

- Glenn Matthews (@glennmatthews)
- Marek Zbroch (@mzbroch)

## Nautobot Features Used

This plugin adds the following data models to Nautobot:

- AutonomousSystem
- PeeringRole
- BGPRoutingInstance
- AddressFamily
- PeerGroupTemplate
- PeerGroup
- PeerGroupAddressFamily
- PeerEndpoint
- PeerEndpointAddressFamily
- Peering

The data models introduced by the BGP plugin support the following Nautobot features:

- Rest API
- GraphQL
- Custom fields
- Custom Links
- Relationships
- Change logging
- Custom data validation logic
- Webhooks

For more details please visit the [BGP Data Models](../dev/models.md) page.
