# Example use of BGP Models app - Cisco BGP Configuration

This document provides an example of generating a Cisco device's desired BGP configuration based on data stored in Nautobot using this app. A GraphQL query is used to retrieve the relevant data, which is then rendered through a Jinja2 template to produce the desired configuration.

## Querying for the data

In order to retrieve a BGP data, following GraphQL query can be issued to Nautobot.

```python
import pynautobot
import json
variables = {"device_id": "0a415303-999b-4222-88b8-ba3fef4cdc33"}
query = """
query ($device_id: ID!) {
    device(id: $device_id) {
        name
        bgp_routing_instances {
            extra_attributes
            autonomous_system {
                asn
            }
            peer_groups {
                name
                extra_attributes
                peergroup_template {
                    autonomous_system {
                        asn
                    }
                    extra_attributes
                }
                address_families {
                    afi_safi
                    import_policy
                    export_policy
                }
            }
            endpoints {
                peer_group {
                    name
                }
                source_ip {
                    address
                }
                peer {
                    source_ip {
                        address
                    }
                    autonomous_system {
                        asn
                    }
                    routing_instance {
                        autonomous_system {
                            asn
                        }
                    }
                }
            }
        }
    }
}
"""
nb = pynautobot.api(
    url="http://localhost:8080",
    token="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
)
gql = nb.graphql.query(query=query, variables=variables)
```

## Retrieving the data

An example data returned from Nautobot is presented below.

```json
{
  "data": {
    "device": {
      "name": "ams01-edge-01",
      "bgp_routing_instances": [
        {
          "extra_attributes": {
            "auto-summary": false,
            "synchronization": false
          },
          "autonomous_system": {
            "asn": 65535
          },
          "peer_groups": [
            {
              "name": "EDGE-to-LEAF",
              "extra_attributes": null,
              "peergroup_template": {
                "autonomous_system": null,
                "extra_attributes": {},
                "role": {
                  "slug": "peer"
                }
              },
              "address_families": [
                {
                  "afi_safi": "IPV4_UNICAST",
                  "import_policy": "BGP-LEAF-IN",
                  "export_policy": "BGP-LEAF-OUT",
                  "extra_attributes": {
                    "next-hop-self": true,
                    "send-community": true,
                  }
                }
              ]
            },
            {
              "name": "EDGE-to-TRANSIT",
              "extra_attributes": null,
              "peergroup_template": {
                "autonomous_system": null,
                "import_policy": "BGP-TRANSIT-IN",
                "export_policy": "BGP-TRANSIT-OUT",
                "extra_attributes": {
                  "ttl_security_hops": 1
                },
                "role": {
                  "slug": "customer"
                }
              },
              "address_families": [
                {
                  "afi_safi": "IPV4_UNICAST",
                  "import_policy": "BGP-TRANSIT-IN",
                  "export_policy": "BGP-TRANSIT-OUT",
                  "extra_attributes": {}
                }
              ]
            }
          ],
          "endpoints": [
            {
              "peer_group": {
                "name": "EDGE-to-LEAF"
              },
              "source_ip": {
                "address": "10.11.192.12/32"
              },
              "peer": {
                "source_ip": {
                  "address": "10.11.192.13/32"
                },
                "autonomous_system": null,
                "routing_instance": {
                  "autonomous_system": {
                    "asn": 4200000000
                  }
                }
              }
            },
            {
              "peer_group": {
                "name": "EDGE-to-LEAF"
              },
              "source_ip": {
                "address": "10.11.192.28/32"
              },
              "peer": {
                "source_ip": {
                  "address": "10.11.192.29/32"
                },
                "autonomous_system": null,
                "routing_instance": {
                  "autonomous_system": {
                    "asn": 4200000000
                  }
                }
              }
            },
            {
              "peer_group": {
                "name": "EDGE-to-LEAF"
              },
              "source_ip": {
                "address": "10.11.192.8/32"
              },
              "peer": {
                "source_ip": {
                  "address": "10.11.192.9/32"
                },
                "autonomous_system": null,
                "routing_instance": {
                  "autonomous_system": {
                    "asn": 4200000000
                  }
                }
              }
            },
            {
              "peer_group": {
                "name": "EDGE-to-LEAF"
              },
              "source_ip": {
                "address": "10.11.192.24/32"
              },
              "peer": {
                "source_ip": {
                  "address": "10.11.192.25/32"
                },
                "autonomous_system": null,
                "routing_instance": {
                  "autonomous_system": {
                    "asn": 4200000000
                  }
                }
              }
            },
            {
              "peer_group": {
                "name": "EDGE-to-LEAF"
              },
              "source_ip": {
                "address": "10.11.192.4/32"
              },
              "peer": {
                "source_ip": {
                  "address": "10.11.192.5/32"
                },
                "autonomous_system": null,
                "routing_instance": {
                  "autonomous_system": {
                    "asn": 4200000000
                  }
                }
              }
            },
            {
              "peer_group": {
                "name": "EDGE-to-LEAF"
              },
              "source_ip": {
                "address": "10.11.192.20/32"
              },
              "peer": {
                "source_ip": {
                  "address": "10.11.192.21/32"
                },
                "autonomous_system": null,
                "routing_instance": {
                  "autonomous_system": {
                    "asn": 4200000000
                  }
                }
              }
            },
            {
              "peer_group": {
                "name": "EDGE-to-LEAF"
              },
              "source_ip": {
                "address": "10.11.192.16/32"
              },
              "peer": {
                "source_ip": {
                  "address": "10.11.192.17/32"
                },
                "autonomous_system": null,
                "routing_instance": {
                  "autonomous_system": {
                    "asn": 4200000000
                  }
                }
              }
            },
            {
              "peer_group": {
                "name": "EDGE-to-LEAF"
              },
              "source_ip": {
                "address": "10.11.192.32/32"
              },
              "peer": {
                "source_ip": {
                  "address": "10.11.192.33/32"
                },
                "autonomous_system": null,
                "routing_instance": {
                  "autonomous_system": {
                    "asn": 4200000000
                  }
                }
              }
            },
            {
              "peer_group": {
                "name": "EDGE-to-TRANSIT"
              },
              "source_ip": {
                "address": "104.94.128.1/29"
              },
              "peer": {
                "source_ip": {
                  "address": "104.94.128.2/29"
                },
                "autonomous_system": {
                  "asn": 1299
                },
                "routing_instance": null
              }
            },
            {
              "peer_group": {
                "name": "EDGE-to-TRANSIT"
              },
              "source_ip": {
                "address": "104.94.128.9/29"
              },
              "peer": {
                "source_ip": {
                  "address": "104.94.128.10/29"
                },
                "autonomous_system": {
                  "asn": 2914
                },
                "routing_instance": null
              }
            }
          ]
        }
      ]
    }
  }
}
```

## Creating a Cisco Jinja2 BGP Configuration Template

Following snippet represents an example Cisco BGP Configuration Template:

```
!
router bgp {{ data.device.bgp_routing_instances.0.autonomous_system.asn }}
{%- for peer_group in data.device.bgp_routing_instances.0.peer_groups %}
 neighbor {{ peer_group.name }} peer-group
 neighbor {{ peer_group.name }} route-map {{ peer_group.address_families.0.import_policy }} in
 neighbor {{ peer_group.name }} route-map {{ peer_group.address_families.0.export_policy }} out
{%- if "next-hop-self" in peer_group.address_families.0.extra_attributes %}
 neighbor {{ peer_group.name }} next-hop-self
{%- endif %}
{%- if "send-community" in peer_group.address_families.0.extra_attributes %}
 neighbor {{ peer_group.name }} send-community
{%- endif %}
{%- if "ttl_security_hops" in peer_group.peergroup_template.extra_attributes %}
 neighbor {{ peer_group.name }} ttl-security hops {{ peer_group.peergroup_template.extra_attributes.ttl_security_hops }}
{%- endif %}
{%- endfor %}
!
{%- for endpoint in data.device.bgp_routing_instances.0.endpoints %}
{%- if endpoint.peer.autonomous_system %}
{%- set remote_asn=endpoint.peer.autonomous_system.asn %}
{%- else %}
{%- set remote_asn=endpoint.peer.routing_instance.autonomous_system.asn %}
{%- endif %}
 neighbor {{ endpoint.peer.source_ip.address | ipaddr('address') }} remote-as {{ remote_asn }}
{%- if endpoint.peer_group %}
 neighbor {{ endpoint.peer.source_ip.address | ipaddr('address') }} peer-group {{ endpoint.peer_group.name }}
{%- endif %}
{%- endfor %}
!
{%- if data.device.bgp_routing_instances.0.extra_attributes.synchronization == false %}
 no synchronization
{%- endif %}
!
```


## Rendering Cisco Jinja2 BGP Configuration Template with the data retrieved from GraphQL

Following snippet represents an example Cisco BGP rendered configuration:

```text
!
router bgp 65535
 neighbor EDGE-to-LEAF peer-group
 neighbor EDGE-to-LEAF route-map BGP-LEAF-IN in
 neighbor EDGE-to-LEAF route-map BGP-LEAF-OUT out
 neighbor EDGE-to-LEAF next-hop-self
 neighbor EDGE-to-LEAF send-community
 neighbor EDGE-to-TRANSIT peer-group
 neighbor EDGE-to-TRANSIT route-map BGP-TRANSIT-IN in
 neighbor EDGE-to-TRANSIT route-map BGP-TRANSIT-OUT out
 neighbor EDGE-to-TRANSIT ttl-security hops 1
!
 neighbor 10.11.192.13 remote-as 4200000000
 neighbor 10.11.192.13 peer-group EDGE-to-LEAF
 neighbor 10.11.192.29 remote-as 4200000000
 neighbor 10.11.192.29 peer-group EDGE-to-LEAF
 neighbor 10.11.192.9 remote-as 4200000000
 neighbor 10.11.192.9 peer-group EDGE-to-LEAF
 neighbor 10.11.192.25 remote-as 4200000000
 neighbor 10.11.192.25 peer-group EDGE-to-LEAF
 neighbor 10.11.192.5 remote-as 4200000000
 neighbor 10.11.192.5 peer-group EDGE-to-LEAF
 neighbor 10.11.192.21 remote-as 4200000000
 neighbor 10.11.192.21 peer-group EDGE-to-LEAF
 neighbor 10.11.192.17 remote-as 4200000000
 neighbor 10.11.192.17 peer-group EDGE-to-LEAF
 neighbor 10.11.192.33 remote-as 4200000000
 neighbor 10.11.192.33 peer-group EDGE-to-LEAF
 neighbor 104.94.128.2 remote-as 1299
 neighbor 104.94.128.2 peer-group EDGE-to-TRANSIT
 neighbor 104.94.128.10 remote-as 2914
 neighbor 104.94.128.10 peer-group EDGE-to-TRANSIT
!
 no synchronization
!
```
