"""
Performance AI MCP Server
Web performance analysis and optimization tools powered by MEOK AI Labs.
"""


import sys, os
sys.path.insert(0, os.path.expanduser('~/clawd/meok-labs-engine/shared'))
from auth_middleware import check_access

import time
from collections import defaultdict
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("performance-ai-mcp")

_call_counts: dict[str, list[float]] = defaultdict(list)
FREE_TIER_LIMIT = 50
WINDOW = 86400


def _check_rate_limit(tool_name: str) -> None:
    now = time.time()
    _call_counts[tool_name] = [t for t in _call_counts[tool_name] if now - t < WINDOW]
    if len(_call_counts[tool_name]) >= FREE_TIER_LIMIT:
        raise ValueError(f"Rate limit exceeded for {tool_name}. Free tier: {FREE_TIER_LIMIT}/day. Upgrade at https://meok.ai/pricing")
    _call_counts[tool_name].append(now)


def _rate_metric(value: float, good: float, poor: float, lower_is_better: bool = True) -> str:
    if lower_is_better:
        return "good" if value <= good else "needs-improvement" if value <= poor else "poor"
    return "good" if value >= good else "needs-improvement" if value >= poor else "poor"


@mcp.tool()
def analyze_waterfall_data(resources: list[dict], api_key: str = "") -> dict:
    """Analyze a resource loading waterfall for performance bottlenecks.

    Args:
        resources: List of resource dicts with keys: url, type (js/css/img/font/html/other), size_kb, start_ms, duration_ms, blocking (bool, optional)
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    _check_rate_limit("analyze_waterfall_data")
    if not resources:
        return {"error": "No resources provided"}
    total_size = sum(r.get("size_kb", 0) for r in resources)
    total_duration = max(r.get("start_ms", 0) + r.get("duration_ms", 0) for r in resources) if resources else 0
    by_type = defaultdict(lambda: {"count": 0, "total_kb": 0.0, "total_ms": 0.0})
    for r in resources:
        t = r.get("type", "other")
        by_type[t]["count"] += 1
        by_type[t]["total_kb"] += r.get("size_kb", 0)
        by_type[t]["total_ms"] += r.get("duration_ms", 0)
    blocking = [r for r in resources if r.get("blocking")]
    blocking_time = sum(r.get("duration_ms", 0) for r in blocking)
    issues = []
    large = [r for r in resources if r.get("size_kb", 0) > 200]
    for r in large:
        issues.append({"issue": f"Large resource: {r.get('url', 'unknown')} ({r.get('size_kb')}KB)",
                        "severity": "warning", "category": "size"})
    slow = [r for r in resources if r.get("duration_ms", 0) > 1000]
    for r in slow:
        issues.append({"issue": f"Slow resource: {r.get('url', 'unknown')} ({r.get('duration_ms')}ms)",
                        "severity": "warning", "category": "latency"})
    if blocking_time > 500:
        issues.append({"issue": f"High render-blocking time: {blocking_time}ms", "severity": "error", "category": "blocking"})
    if len(resources) > 80:
        issues.append({"issue": f"Too many requests: {len(resources)}", "severity": "warning", "category": "requests"})
    return {"total_resources": len(resources), "total_size_kb": round(total_size, 1),
            "total_duration_ms": round(total_duration, 1), "by_type": dict(by_type),
            "blocking_resources": len(blocking), "blocking_time_ms": round(blocking_time, 1),
            "issues": issues}


@mcp.tool()
def suggest_optimizations(page_data: dict, api_key: str = "") -> dict:
    """Suggest performance optimizations based on page characteristics.

    Args:
        page_data: Dict with optional keys: total_size_kb, js_count, css_count, image_count, font_count, uses_http2 (bool), has_service_worker (bool), has_lazy_loading (bool), ttfb_ms, lcp_ms, cls, fid_ms
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    _check_rate_limit("suggest_optimizations")
    suggestions = []
    total = page_data.get("total_size_kb", 0)
    if total > 3000:
        suggestions.append({"category": "size", "priority": "high",
                           "suggestion": f"Page is {total}KB. Target under 1500KB. Compress assets and remove unused code."})
    if page_data.get("js_count", 0) > 15:
        suggestions.append({"category": "javascript", "priority": "high",
                           "suggestion": f"Too many JS files ({page_data['js_count']}). Bundle and code-split."})
    if page_data.get("css_count", 0) > 5:
        suggestions.append({"category": "css", "priority": "medium",
                           "suggestion": f"Multiple CSS files ({page_data['css_count']}). Inline critical CSS and defer the rest."})
    if page_data.get("image_count", 0) > 20 and not page_data.get("has_lazy_loading"):
        suggestions.append({"category": "images", "priority": "high",
                           "suggestion": "Many images without lazy loading. Add loading='lazy' to below-fold images."})
    if page_data.get("font_count", 0) > 3:
        suggestions.append({"category": "fonts", "priority": "medium",
                           "suggestion": f"Too many font files ({page_data['font_count']}). Limit to 2-3 and use font-display: swap."})
    if not page_data.get("uses_http2"):
        suggestions.append({"category": "protocol", "priority": "high",
                           "suggestion": "Enable HTTP/2 for multiplexed connections and header compression."})
    if not page_data.get("has_service_worker"):
        suggestions.append({"category": "caching", "priority": "medium",
                           "suggestion": "Add a service worker for offline support and faster repeat visits."})
    ttfb = page_data.get("ttfb_ms", 0)
    if ttfb > 600:
        suggestions.append({"category": "server", "priority": "high",
                           "suggestion": f"TTFB is {ttfb}ms. Target <200ms. Consider CDN, caching, or server optimization."})
    lcp = page_data.get("lcp_ms", 0)
    if lcp > 2500:
        suggestions.append({"category": "lcp", "priority": "high",
                           "suggestion": f"LCP is {lcp}ms (poor). Preload hero image, optimize critical path."})
    suggestions.sort(key=lambda x: {"high": 0, "medium": 1, "low": 2}.get(x["priority"], 3))
    return {"suggestions": suggestions, "count": len(suggestions),
            "high_priority": sum(1 for s in suggestions if s["priority"] == "high")}


@mcp.tool()
def calculate_core_web_vitals(lcp_ms: float, fid_ms: float, cls: float, inp_ms: float = 0, api_key: str = "") -> dict:
    """Calculate and rate Core Web Vitals scores.

    Args:
        lcp_ms: Largest Contentful Paint in milliseconds
        fid_ms: First Input Delay in milliseconds
        cls: Cumulative Layout Shift score
        inp_ms: Interaction to Next Paint in ms (optional, new metric)
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    _check_rate_limit("calculate_core_web_vitals")
    lcp_rating = _rate_metric(lcp_ms, 2500, 4000)
    fid_rating = _rate_metric(fid_ms, 100, 300)
    cls_rating = _rate_metric(cls, 0.1, 0.25)
    inp_rating = _rate_metric(inp_ms, 200, 500) if inp_ms else "not-measured"
    all_good = lcp_rating == "good" and fid_rating == "good" and cls_rating == "good"
    any_poor = "poor" in (lcp_rating, fid_rating, cls_rating)
    overall = "good" if all_good else "poor" if any_poor else "needs-improvement"
    score = 100
    score_map = {"good": 0, "needs-improvement": -15, "poor": -35}
    score += score_map.get(lcp_rating, 0) + score_map.get(fid_rating, 0) + score_map.get(cls_rating, 0)
    tips = []
    if lcp_rating != "good":
        tips.append("LCP: Preload hero images, optimize server response, remove render-blocking resources")
    if fid_rating != "good":
        tips.append("FID: Break up long tasks, use web workers, reduce JS execution time")
    if cls_rating != "good":
        tips.append("CLS: Set dimensions on images/ads, avoid inserting content above existing content")
    return {"lcp": {"value_ms": lcp_ms, "rating": lcp_rating, "threshold": {"good": 2500, "poor": 4000}},
            "fid": {"value_ms": fid_ms, "rating": fid_rating, "threshold": {"good": 100, "poor": 300}},
            "cls": {"value": cls, "rating": cls_rating, "threshold": {"good": 0.1, "poor": 0.25}},
            "inp": {"value_ms": inp_ms, "rating": inp_rating, "threshold": {"good": 200, "poor": 500}},
            "overall": overall, "score": max(0, score), "tips": tips}


@mcp.tool()
def image_optimization_hints(images: list[dict], api_key: str = "") -> dict:
    """Analyze images and suggest optimization strategies.

    Args:
        images: List of image dicts with keys: url (or name), format (jpg/png/gif/webp/svg), size_kb, width, height, above_fold (bool, optional)
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    _check_rate_limit("image_optimization_hints")
    hints = []
    total_size = 0
    potential_savings = 0
    for img in images:
        size = img.get("size_kb", 0)
        total_size += size
        fmt = img.get("format", "").lower()
        w = img.get("width", 0)
        h = img.get("height", 0)
        name = img.get("url", img.get("name", "unknown"))
        img_hints = []
        if fmt in ("jpg", "jpeg", "png") and fmt != "webp":
            savings = size * 0.3
            img_hints.append(f"Convert to WebP/AVIF for ~30% savings (~{savings:.0f}KB)")
            potential_savings += savings
        if fmt == "png" and size > 100:
            img_hints.append("Consider JPEG if no transparency needed")
        if size > 500:
            img_hints.append(f"Very large image ({size}KB). Compress and resize.")
            potential_savings += size * 0.5
        if w > 2000 or h > 2000:
            img_hints.append(f"Image dimensions very large ({w}x{h}). Serve responsive sizes.")
        if not img.get("above_fold") and size > 50:
            img_hints.append("Below fold - add loading='lazy'")
        if img.get("above_fold"):
            img_hints.append("Above fold - preload with <link rel='preload'>")
        if img_hints:
            hints.append({"image": name[:80], "size_kb": size, "hints": img_hints})
    return {"images_analyzed": len(images), "total_size_kb": round(total_size, 1),
            "potential_savings_kb": round(potential_savings, 1),
            "savings_percent": round(potential_savings / max(total_size, 1) * 100, 1),
            "hints": hints}


if __name__ == "__main__":
    mcp.run()
