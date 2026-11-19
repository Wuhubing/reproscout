#!/usr/bin/env bash
# Install an already-provisioned dedicated Linux host; never purchases resources.
set -euo pipefail
if [[ "$(id -u)" != 0 ]]; then
  echo 'Run as root on the dedicated deployment host.' >&2
  exit 1
fi
for tool in docker caddy systemctl; do command -v "$tool" >/dev/null; done
[[ -x /opt/reproscout/.venv/bin/python ]]
[[ -f /etc/reproscout/server.env ]]
[[ -f /etc/reproscout/images.json ]]
id reproscout >/dev/null 2>&1 || useradd --system --home-dir /var/lib/reproscout --create-home reproscout
usermod -aG docker reproscout
install -d -o reproscout -g reproscout -m 0700 /var/lib/reproscout
chmod 0600 /etc/reproscout/server.env
install -m 0644 /opt/reproscout/deploy/reproscout.service /etc/systemd/system/reproscout.service
systemctl daemon-reload
systemctl enable --now reproscout
printf '%s\n' 'Backend installed. Configure and validate Caddy with the real domain before publishing.'
