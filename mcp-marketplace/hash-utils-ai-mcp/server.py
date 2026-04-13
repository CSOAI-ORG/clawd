"""
Hash Utils AI MCP Server
Hashing, UUID, and ID generation tools powered by MEOK AI Labs.
"""

import hashlib
import hmac
import os
import string
import time
import uuid
from collections import defaultdict
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("hash-utils-ai-mcp")

_call_counts: dict[str, list[float]] = defaultdict(list)
FREE_TIER_LIMIT = 50
WINDOW = 86400

NANOID_ALPHABET = string.ascii_letters + string.digits + "_-"


def _check_rate_limit(tool_name: str) -> None:
    now = time.time()
    _call_counts[tool_name] = [t for t in _call_counts[tool_name] if now - t < WINDOW]
    if len(_call_counts[tool_name]) >= FREE_TIER_LIMIT:
        raise ValueError(f"Rate limit exceeded for {tool_name}. Free tier: {FREE_TIER_LIMIT}/day. Upgrade at https://meok.ai/pricing")
    _call_counts[tool_name].append(now)


@mcp.tool()
def hash_text(text: str, algorithm: str = "sha256", encoding: str = "hex") -> dict:
    """Hash text using various algorithms.

    Args:
        text: Text to hash
        algorithm: Hash algorithm - 'md5', 'sha1', 'sha256', 'sha384', 'sha512', 'sha3_256', 'blake2b'
        encoding: Output encoding - 'hex' or 'base64'
    """
    _check_rate_limit("hash_text")
    algos = {"md5": hashlib.md5, "sha1": hashlib.sha1, "sha256": hashlib.sha256,
             "sha384": hashlib.sha384, "sha512": hashlib.sha512,
             "sha3_256": hashlib.sha3_256, "blake2b": hashlib.blake2b}
    if algorithm not in algos:
        return {"error": f"Unknown algorithm. Available: {', '.join(algos.keys())}"}
    h = algos[algorithm](text.encode('utf-8'))
    if encoding == "base64":
        import base64
        result = base64.b64encode(h.digest()).decode()
    else:
        result = h.hexdigest()
    return {"hash": result, "algorithm": algorithm, "encoding": encoding,
            "input_length": len(text), "hash_length": len(result)}


@mcp.tool()
def verify_hash(text: str, expected_hash: str, algorithm: str = "sha256") -> dict:
    """Verify if a text matches an expected hash.

    Args:
        text: Text to verify
        expected_hash: Expected hash value
        algorithm: Hash algorithm used (default 'sha256')
    """
    _check_rate_limit("verify_hash")
    algos = {"md5": hashlib.md5, "sha1": hashlib.sha1, "sha256": hashlib.sha256,
             "sha384": hashlib.sha384, "sha512": hashlib.sha512}
    if algorithm not in algos:
        return {"error": f"Unknown algorithm. Available: {', '.join(algos.keys())}"}
    computed = algos[algorithm](text.encode('utf-8')).hexdigest()
    match = hmac.compare_digest(computed.lower(), expected_hash.lower())
    return {"match": match, "algorithm": algorithm, "computed_hash": computed}


@mcp.tool()
def generate_uuid(version: int = 4, count: int = 1, namespace: str = "", name: str = "") -> dict:
    """Generate UUID(s) of various versions.

    Args:
        version: UUID version - 1 (time-based), 3 (MD5 namespace), 4 (random), 5 (SHA1 namespace)
        count: Number of UUIDs to generate (default 1, max 50)
        namespace: Namespace UUID for v3/v5 (use 'dns', 'url', 'oid', or custom UUID)
        name: Name string for v3/v5
    """
    _check_rate_limit("generate_uuid")
    count = min(count, 50)
    ns_map = {"dns": uuid.NAMESPACE_DNS, "url": uuid.NAMESPACE_URL, "oid": uuid.NAMESPACE_OID}
    uuids = []
    for _ in range(count):
        if version == 1:
            u = uuid.uuid1()
        elif version == 3:
            ns = ns_map.get(namespace.lower(), uuid.UUID(namespace) if namespace else uuid.NAMESPACE_DNS)
            u = uuid.uuid3(ns, name or "default")
        elif version == 5:
            ns = ns_map.get(namespace.lower(), uuid.UUID(namespace) if namespace else uuid.NAMESPACE_DNS)
            u = uuid.uuid5(ns, name or "default")
        else:
            u = uuid.uuid4()
        uuids.append(str(u))
    return {"uuids": uuids if count > 1 else uuids[0], "version": version, "count": count}


@mcp.tool()
def generate_nanoid(size: int = 21, alphabet: str = "", count: int = 1) -> dict:
    """Generate nanoid-style short unique identifiers.

    Args:
        size: Length of the ID (default 21)
        alphabet: Custom alphabet (default: A-Za-z0-9_-)
        count: Number of IDs to generate (default 1, max 50)
    """
    _check_rate_limit("generate_nanoid")
    count = min(count, 50)
    size = min(size, 128)
    alpha = alphabet or NANOID_ALPHABET
    ids = []
    for _ in range(count):
        random_bytes = os.urandom(size)
        nid = ''.join(alpha[b % len(alpha)] for b in random_bytes)
        ids.append(nid)
    collision_bits = size * (len(alpha).bit_length())
    return {"ids": ids if count > 1 else ids[0], "size": size,
            "alphabet_size": len(alpha), "count": count,
            "estimated_collision_resistance": f"~{collision_bits} bits"}


if __name__ == "__main__":
    mcp.run()
