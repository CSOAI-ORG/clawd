"""
Compression AI MCP Server
Data compression analysis and optimization tools powered by MEOK AI Labs.
"""

import gzip
import zlib
import bz2
import time
import base64
from collections import defaultdict
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("compression-ai-mcp")

_call_counts: dict[str, list[float]] = defaultdict(list)
FREE_TIER_LIMIT = 50
WINDOW = 86400


def _check_rate_limit(tool_name: str) -> None:
    now = time.time()
    _call_counts[tool_name] = [t for t in _call_counts[tool_name] if now - t < WINDOW]
    if len(_call_counts[tool_name]) >= FREE_TIER_LIMIT:
        raise ValueError(f"Rate limit exceeded for {tool_name}. Free tier: {FREE_TIER_LIMIT}/day. Upgrade at https://meok.ai/pricing")
    _call_counts[tool_name].append(now)


ALGO_INFO = {
    "gzip": {"speed": "medium", "ratio": "good", "use_case": "General purpose, HTTP compression"},
    "zlib": {"speed": "medium", "ratio": "good", "use_case": "In-memory compression, network protocols"},
    "bz2": {"speed": "slow", "ratio": "excellent", "use_case": "Archiving, when ratio matters more than speed"},
    "lzma": {"speed": "very_slow", "ratio": "best", "use_case": "Maximum compression, .xz archives"},
    "lz4": {"speed": "fastest", "ratio": "fair", "use_case": "Real-time compression, databases"},
    "zstd": {"speed": "fast", "ratio": "very_good", "use_case": "Modern general purpose, replaces gzip"},
    "snappy": {"speed": "fastest", "ratio": "fair", "use_case": "Google services, database storage"},
    "brotli": {"speed": "medium", "ratio": "very_good", "use_case": "Web content, HTTP compression"},
}


@mcp.tool()
def estimate_ratio(data: str, algorithms: list[str] | None = None) -> dict:
    """Estimate compression ratios for data using multiple algorithms.

    Args:
        data: Text data to compress (or base64-encoded binary)
        algorithms: List of algorithms to test (default: gzip, zlib, bz2)
    """
    _check_rate_limit("estimate_ratio")
    try:
        raw = base64.b64decode(data)
    except Exception:
        raw = data.encode('utf-8')
    original_size = len(raw)
    if original_size == 0:
        return {"error": "Empty data"}
    algos = algorithms or ["gzip", "zlib", "bz2"]
    results = {}
    compressors = {"gzip": gzip.compress, "zlib": zlib.compress, "bz2": bz2.compress}
    try:
        import lzma
        compressors["lzma"] = lzma.compress
    except ImportError:
        pass
    for algo in algos:
        if algo not in compressors:
            results[algo] = {"error": f"Not available. Supported: {', '.join(compressors.keys())}"}
            continue
        start = time.time()
        compressed = compressors[algo](raw)
        elapsed = time.time() - start
        comp_size = len(compressed)
        results[algo] = {"compressed_size": comp_size, "ratio": round(comp_size / original_size, 4),
                         "savings_pct": round((1 - comp_size / original_size) * 100, 1),
                         "time_ms": round(elapsed * 1000, 2)}
    best = min((r for r in results.values() if isinstance(r, dict) and "ratio" in r), key=lambda x: x["ratio"], default=None)
    return {"original_size": original_size, "results": results,
            "best_ratio": best["ratio"] if best else None}


@mcp.tool()
def suggest_algorithm(data_type: str, priority: str = "balanced", size_mb: float = 1.0) -> dict:
    """Suggest the best compression algorithm for a given use case.

    Args:
        data_type: Type of data - 'text', 'json', 'binary', 'image', 'video', 'database', 'logs', 'web'
        priority: Optimization priority - 'speed', 'ratio', 'balanced'
        size_mb: Approximate data size in MB
    """
    _check_rate_limit("suggest_algorithm")
    recommendations = {
        ("text", "speed"): ["lz4", "zstd", "snappy"],
        ("text", "ratio"): ["bz2", "lzma", "brotli"],
        ("text", "balanced"): ["zstd", "gzip", "brotli"],
        ("json", "speed"): ["lz4", "zstd", "snappy"],
        ("json", "ratio"): ["brotli", "zstd", "bz2"],
        ("json", "balanced"): ["zstd", "brotli", "gzip"],
        ("binary", "speed"): ["lz4", "snappy", "zstd"],
        ("binary", "ratio"): ["lzma", "bz2", "zstd"],
        ("binary", "balanced"): ["zstd", "gzip", "zlib"],
        ("image", "speed"): ["lz4", "snappy"],
        ("image", "ratio"): ["lzma", "bz2"],
        ("image", "balanced"): ["zstd", "gzip"],
        ("logs", "speed"): ["lz4", "zstd"],
        ("logs", "ratio"): ["bz2", "lzma", "brotli"],
        ("logs", "balanced"): ["zstd", "gzip"],
        ("web", "speed"): ["brotli", "gzip"],
        ("web", "ratio"): ["brotli", "zstd"],
        ("web", "balanced"): ["brotli", "gzip", "zstd"],
        ("database", "speed"): ["lz4", "snappy", "zstd"],
        ("database", "ratio"): ["zstd", "lzma"],
        ("database", "balanced"): ["zstd", "lz4"],
    }
    key = (data_type.lower(), priority.lower())
    suggested = recommendations.get(key, ["gzip", "zstd"])
    primary = suggested[0]
    algo_details = [{"algorithm": a, **(ALGO_INFO.get(a, {}))} for a in suggested]
    notes = []
    if size_mb > 100:
        notes.append("For large data, avoid lzma/bz2 (very slow). Prefer zstd or lz4.")
    if data_type == "image":
        notes.append("Already-compressed images (JPEG/PNG) won't compress much further.")
    if data_type == "video":
        notes.append("Video is already compressed. Archival only with zstd or lz4.")
    return {"primary_recommendation": primary, "alternatives": suggested[1:],
            "details": algo_details, "data_type": data_type, "priority": priority, "notes": notes}


@mcp.tool()
def calculate_savings(original_size_mb: float, compressed_size_mb: float, file_count: int = 1) -> dict:
    """Calculate storage and bandwidth savings from compression.

    Args:
        original_size_mb: Original size in MB
        compressed_size_mb: Compressed size in MB
        file_count: Number of similar files (for total savings estimate)
    """
    _check_rate_limit("calculate_savings")
    if original_size_mb <= 0:
        return {"error": "Original size must be positive"}
    savings_mb = original_size_mb - compressed_size_mb
    ratio = compressed_size_mb / original_size_mb
    savings_pct = (1 - ratio) * 100
    total_savings_mb = savings_mb * file_count
    total_savings_gb = total_savings_mb / 1024
    cost_per_gb = 0.023  # approximate S3 pricing
    monthly_savings_usd = total_savings_gb * cost_per_gb
    bandwidth_cost = 0.09  # per GB
    bandwidth_savings_usd = total_savings_gb * bandwidth_cost
    return {"compression_ratio": round(ratio, 4), "savings_percent": round(savings_pct, 1),
            "savings_per_file_mb": round(savings_mb, 2), "total_savings_mb": round(total_savings_mb, 2),
            "total_savings_gb": round(total_savings_gb, 3), "file_count": file_count,
            "estimated_monthly_storage_savings_usd": round(monthly_savings_usd, 4),
            "estimated_bandwidth_savings_per_transfer_usd": round(bandwidth_savings_usd, 4)}


@mcp.tool()
def benchmark_data(data: str) -> dict:
    """Benchmark compression of data across all available algorithms.

    Args:
        data: Text data to benchmark (max 1MB recommended)
    """
    _check_rate_limit("benchmark_data")
    raw = data.encode('utf-8')
    original_size = len(raw)
    if original_size > 1_048_576:
        raw = raw[:1_048_576]
        original_size = len(raw)
    compressors = {"gzip": gzip.compress, "zlib": zlib.compress, "bz2": bz2.compress}
    try:
        import lzma
        compressors["lzma"] = lzma.compress
    except ImportError:
        pass
    results = []
    for name, func in compressors.items():
        start = time.time()
        compressed = func(raw)
        comp_time = time.time() - start
        decomp_func = {"gzip": gzip.decompress, "zlib": zlib.decompress, "bz2": bz2.decompress}.get(name)
        if not decomp_func and name == "lzma":
            import lzma
            decomp_func = lzma.decompress
        start = time.time()
        if decomp_func:
            decomp_func(compressed)
        decomp_time = time.time() - start
        results.append({"algorithm": name, "compressed_size": len(compressed),
                        "ratio": round(len(compressed) / original_size, 4),
                        "savings_pct": round((1 - len(compressed) / original_size) * 100, 1),
                        "compress_ms": round(comp_time * 1000, 2),
                        "decompress_ms": round(decomp_time * 1000, 2),
                        "throughput_mb_s": round(original_size / max(comp_time, 0.0001) / 1_048_576, 1)})
    results.sort(key=lambda x: x["ratio"])
    return {"original_size": original_size, "benchmarks": results,
            "best_ratio": results[0]["algorithm"] if results else None,
            "fastest": min(results, key=lambda x: x["compress_ms"])["algorithm"] if results else None}


if __name__ == "__main__":
    mcp.run()
