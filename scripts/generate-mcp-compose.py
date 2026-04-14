#!/usr/bin/env python3
"""Generate docker-compose.mcp-ensemble.yml from MCP_DEPLOYMENT_MANIFEST.json."""

import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST_PATH = os.path.join(BASE_DIR, "MCP_DEPLOYMENT_MANIFEST.json")
OUTPUT_PATH = os.path.join(BASE_DIR, "docker-compose.mcp-ensemble.yml")


def uses_fastmcp(server_py_path: str) -> bool:
    try:
        with open(server_py_path, "r", encoding="utf-8") as f:
            content = f.read()
        return "FastMCP" in content
    except Exception:
        return False


def main() -> int:
    if not os.path.exists(MANIFEST_PATH):
        print(f"Manifest not found: {MANIFEST_PATH}")
        return 1

    with open(MANIFEST_PATH, "r") as f:
        manifest = json.load(f)

    servers = [s for s in manifest.get("deployable_servers", []) if s.get("deployment_ready")]
    print(f"Generating compose file for {len(servers)} deployable servers...")

    fastmcp_count = 0
    bridge_count = 0

    lines = [
        "# Auto-generated MCP Ensemble Docker Compose",
        f"# Generated from: {os.path.basename(MANIFEST_PATH)}",
        f"# Total servers: {len(servers)}",
        "",
        "name: mcp-ensemble",
        "",
        "networks:",
        "  mcp-ensemble:",
        "    driver: bridge",
        "",
        "services:",
    ]

    base_port = 8000
    for idx, server in enumerate(servers):
        name = server["name"]
        repo_dir = f"./mcp-marketplace/{name}"
        external_port = base_port + idx
        server_py = os.path.join(BASE_DIR, "mcp-marketplace", name, "server.py")

        if uses_fastmcp(server_py):
            cmd = (
                'sh -c "uv pip install -e . && '
                'python -c \\\"from server import mcp; mcp.settings.host=\'0.0.0.0\'; mcp.run(transport=\'sse\')\\\""'
            )
            fastmcp_count += 1
        else:
            cmd = (
                'sh -c "uv pip install -e . && '
                'python /home/nicholas/mcp-sse-bridge.py"'
            )
            bridge_count += 1

        lines.extend([
            f"  {name}:",
            f"    container_name: {name}",
            f"    build:",
            f"      context: {repo_dir}",
            f"      dockerfile: ../../Dockerfile.mcp-base",
            f"    working_dir: /app",
            f"    command: >",
            f"      {cmd}",
            f"    ports:",
            f"      - \"{external_port}:8000\"",
            f"    volumes:",
            f"      - {repo_dir}:/app",
            f"      - ./meok-labs-engine/shared:/home/nicholas/clawd/meok-labs-engine/shared:ro",
            f"    networks:",
            f"      - mcp-ensemble",
            f"    restart: unless-stopped",
            f"    profiles:",
            f"      - mcp",
            f"    healthcheck:",
            f"      test: [\"CMD-SHELL\", \"python -c \\\"import urllib.request; urllib.request.urlopen('http://localhost:8000/sse')\\\" || exit 1\"]",
            f"      interval: 30s",
            f"      timeout: 10s",
            f"      retries: 3",
            f"      start_period: 15s",
            "",
        ])

    with open(OUTPUT_PATH, "w") as f:
        f.write("\n".join(lines))

    print(f"Wrote {len(lines)} lines to {OUTPUT_PATH}")
    print(f"Port range: {base_port} -> {base_port + len(servers) - 1}")
    print(f"FastMCP services: {fastmcp_count}, Bridge services: {bridge_count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
