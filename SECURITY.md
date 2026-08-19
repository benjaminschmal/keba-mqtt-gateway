# Security Policy

## Reporting a vulnerability

Please do not disclose security vulnerabilities in public issues.

Report security issues privately to the repository owner through GitHub. Include enough detail to reproduce the issue and, where possible, a suggested mitigation.

## Credentials

Never commit MQTT passwords, API tokens, private keys, or other secrets to this repository. Use environment variables or a local `.env` file that is excluded from Git.

The gateway is designed for a trusted home/local network. If exposed beyond the local network, put appropriate authentication and network controls in front of the web interface and MQTT broker.
