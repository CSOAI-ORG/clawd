#!/usr/bin/env python3
"""Generic SSE bridge for low-level mcp.server.Server instances.

Usage from a repo directory:
    python /path/to/mcp-sse-bridge.py

This imports `server` from `server.py` and exposes it over SSE.
"""

import sys
import os

# Ensure shared auth middleware is available
sys.path.insert(0, os.path.expanduser("~/clawd/meok-labs-engine/shared"))

# Import the low-level server from the current working directory
sys.path.insert(0, os.getcwd())
from server import server as mcp_server

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Mount, Route
from mcp.server.sse import SseServerTransport


SSE_PATH = "/sse"
MESSAGE_PATH = "/messages/"

sse = SseServerTransport(MESSAGE_PATH)


async def handle_sse(scope, receive, send):
    async with sse.connect_sse(scope, receive, send) as streams:
        await mcp_server.run(
            streams[0],
            streams[1],
            mcp_server.create_initialization_options(),
        )
    return Response()


async def sse_endpoint(request: Request) -> Response:
    return await handle_sse(request.scope, request.receive, request._send)


app = Starlette(
    routes=[
        Route(SSE_PATH, endpoint=sse_endpoint, methods=["GET"]),
        Mount(MESSAGE_PATH, app=sse.handle_post_message),
    ],
)

if __name__ == "__main__":
    import uvicorn
    host = os.environ.get("MCP_HOST", "0.0.0.0")
    port = int(os.environ.get("MCP_PORT", "8000"))
    uvicorn.run(app, host=host, port=port, log_level="info")
