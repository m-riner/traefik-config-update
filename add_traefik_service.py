#!/usr/bin/env python3
"""
Traefik Service Configurator
Automatically adds HTTP routers and services to a Traefik file provider configuration.
Preserves existing YAML formatting and comments using ruamel.yaml.
"""

import sys
import argparse
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap

# Path to your Traefik dynamic configuration file
CONFIG_PATH = "/etc/traefik/conf.d/services.yaml"


def add_service(name, rule, target_url):
    """Parses the YAML file and injects the new router and service blocks."""
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.indent(mapping=2, sequence=4, offset=2)

    # Load the existing configuration file
    try:
        with open(CONFIG_PATH, "r") as f:
            config = yaml.load(f)
    except FileNotFoundError:
        config = None
    except Exception as e:
        print(f"Error reading config file: {e}")
        sys.exit(1)

    # If the file is completely empty, initialize a new CommentedMap
    if config is None:
        config = CommentedMap()

    # Ensure the basic Traefik HTTP structure exists
    if "http" not in config: config["http"] = CommentedMap()
    if "routers" not in config["http"]: config["http"]["routers"] = CommentedMap()
    if "services" not in config["http"]: config["http"]["services"] = CommentedMap()

    routers = config["http"]["routers"]
    services = config["http"]["services"]

    # Check if the router or service name already exists
    if name in routers or f"{name}-service" in services:
        print(f"Error: A service or router named '{name}' already exists!")
        sys.exit(1)

    # Determine the number for the section comment
    next_number = len(routers) + 1

    # Create the new router block
    new_router = CommentedMap({
        "rule": rule,
        "entryPoints": ["websecure"],
        "service": f"{name}-service",
        "tls": CommentedMap()
    })
    
    # Add inline comment for the TLS block
    new_router["tls"].yaml_add_eol_comment("Automatically uses the wildcard certificate configured above", column=14)

    # Insert the router and place a numbered heading comment above it
    routers[name] = new_router
    routers.yaml_set_comment_before_after_key(name, before=f"{next_number}. {name.capitalize()}")

    # Create the new service (backend/load balancer) block
    new_service = {
        "loadBalancer": {
            "servers": [
                {"url": target_url}
            ]
        }
    }
    services[f"{name}-service"] = new_service

    # Write the updated configuration back to the file
    try:
        with open(CONFIG_PATH, "w") as f:
            yaml.dump(config, f)
        print(f"Successfully added: {name} ({rule} -> {target_url})")
    except Exception as e:
        print(f"Error writing to config file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Dynamically add new services to Traefik file provider configuration.")
    parser.add_argument("--name", required=True, help="Unique identifier for the Traefik router/service (e.g., proxmox)")
    parser.add_argument("--rule", required=True, help="Full Traefik routing rule, e.g., 'Host(`localhost.local`)'")
    parser.add_argument("--url", required=True, help="Target backend URL with port, e.g., 'http://0.0.0.0:8080'")

    args = parser.parse_args()
    add_service(args.name, args.rule, args.url)