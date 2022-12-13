# App Overview

This document provides an overview of the App including critical information and import considerations when applying it to your Nautobot environment.

!!! note
    Throughout this documentation, the terms "app" and "plugin" will be used interchangeably.

## Description

An app for [Nautobot](https://github.com/nautobot/nautobot), extending the core models with BGP-specific models. They enable modeling and management of BGP peerings, whether or not the peer device is present in Nautobot.

## Audience (User Personas) - Who should use this App?

Network Admins who need to model their BGP internal and external peerings inside of their Source of Truth so they can programmatically generate BGP configuration for their devices.

## Authors and Maintainers

## Nautobot Features Used

This plugin adds the following data models to Nautobot:

- AutonomousSystem
- BGPRoutingInstance
- PeerEndpoint
- PeerGroup
- PeerGroupTemplate
- AddressFamily
- Peering
- PeeringRole

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
