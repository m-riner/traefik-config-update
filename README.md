# traefik-config-update
A lightweight, robust Python automation script designed to update your Traefik Reverse Proxy file provider configuration on the fly. This tool allows you to treat your Traefik routing rules strictly as code, making it a perfect fit for CI/CD pipelines, automated LXC/Docker provisioning scripts, or homelab GitOps workflows.



### Prerequisites
Install the required dependency using pip:
```bash
pip3 install ruamel.yaml

```
### Usage
```bash
python3 add_traefik_service.py --name null --rule 'Host(`localhost.local`)' --url http://0.0.0.0:8080
