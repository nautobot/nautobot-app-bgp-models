# Example use of BGP Models plugin - Juniper BGP Configuration

This document provides an example of generating a Juniper device's desired BGP configuration based on data stored in Nautobot using this plugin. A GraphQL query is used to retrieve the relevant data, which is then rendered through a Jinja2 template to produce the desired configuration.

## Querying for the data

To retrieve BGP data, the following GraphQL query can be issued to Nautobot.

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
                    role {
                        slug
                    }
                    extra_attributes
                }
                address_families {
                    afi_safi
                    import_policy
                    export_policy
                    extra_attributes
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
                "role": {
                  "slug": "peer"
                }
                "extra_attributes": {}
              },
              "address_families": [
                {
                  "afi_safi": "IPV4_UNICAST",
                  "import_policy": "BGP-LEAF-IN",
                  "export_policy": "BGP-LEAF-OUT",
                  "extra_attributes": {
                    "next-hop-self": true,
                    "send-community": true
                  }
                }
              ]
            },
            {
              "name": "EDGE-to-TRANSIT",
              "extra_attributes": null,
              "peergroup_template": {
                "autonomous_system": null,
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

## Creating a Juniper Jinja2 BGP Configuration Template

Following snippet represents an example Juniper BGP Configuration Template:

```
# Set the ASN for Routing Instance
set routing-options autonomous-system {{ data.device.bgp_routing_instances.0.autonomous_system.asn }}

# Configure Groups
{%- for peer_group in data.device.bgp_routing_instances.0.peer_groups %}
{%- if peer_group.peergroup_template.role.slug == "peer" %}
set protocols bgp group {{ peer_group.name }} type internal
{%- endif %}
{%- if peer_group.peergroup_template.role.slug == "customer" %}
set protocols bgp group {{ peer_group.name }} type external
{%- endif %}
set protocols bgp group {{ peer_group.name }} import {{ peer_group.address_families.0.import_policy }}
set protocols bgp group {{ peer_group.name }} export {{ peer_group.address_families.0.export_policy }}
{%- endfor %}

# Configure Peers
{%- for endpoint in data.device.bgp_routing_instances.0.endpoints %}
{%- if endpoint.peer.autonomous_system %}
{%- set remote_asn=endpoint.peer.autonomous_system.asn %}
{%- else %}
{%- set remote_asn=endpoint.peer.routing_instance.autonomous_system.asn %}
{%- endif %}
set protocols bgp group {{ endpoint.peer_group.name }} neighbor {{ endpoint.peer.source_ip.address | ipaddr('address') }} peer-as {{ remote_asn }}
{%- endfor %}
#
```


## Rendering Juniper Jinja2 BGP Configuration Template with the data retrieved from GraphQL

Following snippet represents an example Juniper BGP Renderer Configuration:

```text
root# show protocols bgp
group EDGE-to-LEAF {
    type internal;
    import BGP-LEAF-IN;
    export BGP-LEAF-OUT;
    local-as 4200000000;
    neighbor 10.11.192.13 {
        peer-as 4200000000;
    }
    neighbor 10.11.192.29 {
        peer-as 4200000000;
    }
    neighbor 10.11.192.9 {
        peer-as 4200000000;
    }
    neighbor 10.11.192.25 {
        peer-as 4200000000;
    }
    neighbor 10.11.192.5 {
        peer-as 4200000000;
    }
    neighbor 10.11.192.21 {
        peer-as 4200000000;
    }
    neighbor 10.11.192.17 {
        peer-as 4200000000;
    }
    neighbor 10.11.192.33 {
        peer-as 4200000000;
    }
}
group EDGE-to-TRANSIT {
    type external;
    import BGP-TRANSIT-IN;
    export BGP-TRANSIT-OUT;
    neighbor 104.94.128.2 {
        peer-as 1299;
    }
    neighbor 104.94.128.10 {
        peer-as 2914;
    }
}

[edit]

root# show routing-options
autonomous-system 65535;

[edit]
```
