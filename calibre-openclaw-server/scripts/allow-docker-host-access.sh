#!/usr/bin/env bash
set -euo pipefail

PORT="${1:-6180}"

if [[ "$(id -u)" -ne 0 ]]; then
  echo "Run as root: sudo $0 ${PORT}" >&2
  exit 1
fi

add_rule() {
  local iface="$1"

  if iptables -C INPUT -i "$iface" -p tcp --dport "$PORT" -j ACCEPT 2>/dev/null; then
    echo "Rule already exists for ${iface}:${PORT}"
    return
  fi

  iptables -I INPUT 1 -i "$iface" -p tcp --dport "$PORT" -j ACCEPT
  echo "Allowed TCP ${PORT} from interface ${iface}"
}

add_rule docker0
add_rule "br+"

echo
echo "Test from the sandbox container:"
echo "  curl http://host.docker.internal:${PORT}/docs"
