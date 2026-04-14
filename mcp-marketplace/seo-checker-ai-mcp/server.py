"""
SEO Checker AI MCP Server
SEO analysis and optimization tools powered by MEOK AI Labs.
"""


import sys, os
sys.path.insert(0, os.path.expanduser('~/clawd/meok-labs-engine/shared'))
from auth_middleware import check_access

import re
import time
from collections import defaultdict
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("seo-checker-ai-mcp")

_call_counts: dict[str, list[float]] = defaultdict(list)
FREE_TIER_LIMIT = 50
WINDOW = 86400


def _check_rate_limit(tool_name: str) -> None:
    now = time.time()
    _call_counts[tool_name] = [t for t in _call_counts[tool_name] if now - t < WINDOW]
    if len(_call_counts[tool_name]) >= FREE_TIER_LIMIT:
        raise ValueError(f"Rate limit exceeded for {tool_name}. Free tier: {FREE_TIER_LIMIT}/day. Upgrade at https://meok.ai/pricing")
    _call_counts[tool_name].append(now)


@mcp.tool()
def analyze_title(title: str, target_keyword: str = "", api_key: str = "") -> dict:
    """Analyze a page title for SEO best practices.

    Args:
        title: Page title tag content
        target_keyword: Optional target keyword to check placement
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    _check_rate_limit("analyze_title")
    issues = []
    length = len(title)
    if length == 0:
        issues.append({"issue": "Title is empty", "severity": "error"})
    elif length < 30:
        issues.append({"issue": f"Title too short ({length} chars). Aim for 50-60.", "severity": "warning"})
    elif length > 60:
        issues.append({"issue": f"Title too long ({length} chars). May be truncated in SERPs at ~60.", "severity": "warning"})
    if title and title[0].islower():
        issues.append({"issue": "Title should start with a capital letter", "severity": "info"})
    keyword_info = {}
    if target_keyword:
        kw_lower = target_keyword.lower()
        title_lower = title.lower()
        keyword_info["present"] = kw_lower in title_lower
        keyword_info["position"] = title_lower.find(kw_lower)
        keyword_info["at_start"] = title_lower.startswith(kw_lower)
        if not keyword_info["present"]:
            issues.append({"issue": f"Target keyword '{target_keyword}' not in title", "severity": "warning"})
        elif not keyword_info["at_start"]:
            issues.append({"issue": "Target keyword not at start of title (ideal for SEO)", "severity": "info"})
    power_words = ["best", "guide", "how", "top", "review", "free", "new", "ultimate", "complete"]
    has_power = any(w in title.lower().split() for w in power_words)
    word_count = len(title.split())
    score = 100
    for issue in issues:
        if issue["severity"] == "error":
            score -= 30
        elif issue["severity"] == "warning":
            score -= 15
        else:
            score -= 5
    score = max(0, min(100, score))
    return {"title": title, "length": length, "word_count": word_count, "score": score,
            "has_power_words": has_power, "keyword": keyword_info, "issues": issues}


@mcp.tool()
def check_meta_description(description: str, target_keyword: str = "", api_key: str = "") -> dict:
    """Check a meta description for SEO best practices.

    Args:
        description: Meta description content
        target_keyword: Optional target keyword to check for
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    _check_rate_limit("check_meta_description")
    issues = []
    length = len(description)
    if length == 0:
        issues.append({"issue": "Meta description is empty", "severity": "error"})
    elif length < 120:
        issues.append({"issue": f"Too short ({length} chars). Aim for 150-160.", "severity": "warning"})
    elif length > 160:
        issues.append({"issue": f"Too long ({length} chars). Will be truncated at ~160.", "severity": "warning"})
    if description and not description.rstrip().endswith(('.', '!', '?')):
        issues.append({"issue": "Should end with punctuation", "severity": "info"})
    keyword_info = {}
    if target_keyword:
        keyword_info["present"] = target_keyword.lower() in description.lower()
        if not keyword_info["present"]:
            issues.append({"issue": f"Target keyword '{target_keyword}' not in description", "severity": "warning"})
    cta_words = ["learn", "discover", "find", "get", "try", "start", "read", "explore", "shop", "buy"]
    has_cta = any(w in description.lower() for w in cta_words)
    if not has_cta:
        issues.append({"issue": "Consider adding a call-to-action", "severity": "info"})
    score = 100
    for issue in issues:
        score -= {"error": 30, "warning": 15, "info": 5}.get(issue["severity"], 0)
    return {"description": description, "length": length, "score": max(0, score),
            "has_call_to_action": has_cta, "keyword": keyword_info, "issues": issues}


@mcp.tool()
def validate_schema_markup(json_ld: str, api_key: str = "") -> dict:
    """Validate JSON-LD structured data/schema markup.

    Args:
        json_ld: JSON-LD structured data string
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    _check_rate_limit("validate_schema_markup")
    import json
    try:
        data = json.loads(json_ld)
    except json.JSONDecodeError as e:
        return {"valid": False, "error": f"Invalid JSON: {e}"}
    issues = []
    if isinstance(data, list):
        items = data
    else:
        items = [data]
    for i, item in enumerate(items):
        prefix = f"Item[{i}]" if len(items) > 1 else ""
        if "@context" not in item:
            issues.append({"issue": f"{prefix} Missing @context", "severity": "error"})
        elif "schema.org" not in str(item["@context"]):
            issues.append({"issue": f"{prefix} @context should reference schema.org", "severity": "warning"})
        if "@type" not in item:
            issues.append({"issue": f"{prefix} Missing @type", "severity": "error"})
        schema_type = item.get("@type", "")
        required_fields = {
            "Article": ["headline", "author", "datePublished"],
            "Product": ["name", "description"],
            "Organization": ["name", "url"],
            "Person": ["name"],
            "BreadcrumbList": ["itemListElement"],
            "FAQPage": ["mainEntity"],
            "LocalBusiness": ["name", "address"],
            "Event": ["name", "startDate", "location"],
            "Recipe": ["name", "recipeIngredient"],
            "Review": ["itemReviewed", "reviewRating"],
        }
        if schema_type in required_fields:
            for field in required_fields[schema_type]:
                if field not in item:
                    issues.append({"issue": f"{prefix} {schema_type} missing recommended field: {field}", "severity": "warning"})
    types_found = [item.get("@type", "unknown") for item in items]
    return {"valid": not any(i["severity"] == "error" for i in issues), "issues": issues,
            "types_found": types_found, "item_count": len(items)}


@mcp.tool()
def heading_analysis(html: str, target_keyword: str = "", api_key: str = "") -> dict:
    """Analyze heading structure for SEO optimization.

    Args:
        html: HTML content to analyze
        target_keyword: Optional target keyword
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    _check_rate_limit("heading_analysis")
    headings = []
    for match in re.finditer(r'<h([1-6])[^>]*>(.*?)</h\1>', html, re.IGNORECASE | re.DOTALL):
        level = int(match.group(1))
        text = re.sub(r'<[^>]+>', '', match.group(2)).strip()
        headings.append({"level": level, "text": text})
    issues = []
    h1s = [h for h in headings if h["level"] == 1]
    if len(h1s) == 0:
        issues.append({"issue": "No H1 tag found", "severity": "error"})
    elif len(h1s) > 1:
        issues.append({"issue": f"Multiple H1 tags ({len(h1s)}). Use only one.", "severity": "warning"})
    if h1s and len(h1s[0]["text"]) > 70:
        issues.append({"issue": "H1 is too long. Keep under 70 characters.", "severity": "warning"})
    keyword_in_headings = {}
    if target_keyword:
        kw = target_keyword.lower()
        for h in headings:
            if kw in h["text"].lower():
                keyword_in_headings[f"h{h['level']}"] = keyword_in_headings.get(f"h{h['level']}", 0) + 1
        if not keyword_in_headings:
            issues.append({"issue": f"Target keyword not found in any heading", "severity": "warning"})
        elif "h1" not in keyword_in_headings:
            issues.append({"issue": "Target keyword not in H1", "severity": "warning"})
    level_counts = defaultdict(int)
    for h in headings:
        level_counts[f"h{h['level']}"] += 1
    score = 100
    for issue in issues:
        score -= {"error": 25, "warning": 10, "info": 5}.get(issue["severity"], 0)
    return {"headings": headings, "heading_count": len(headings), "level_distribution": dict(level_counts),
            "keyword_in_headings": keyword_in_headings, "issues": issues, "score": max(0, score)}


if __name__ == "__main__":
    mcp.run()
