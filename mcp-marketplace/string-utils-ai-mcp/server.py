"""
String Utils AI MCP Server
String manipulation and transformation tools powered by MEOK AI Labs.
"""


import sys, os
sys.path.insert(0, os.path.expanduser('~/clawd/meok-labs-engine/shared'))
from auth_middleware import check_access

import re
import time
import unicodedata
from collections import defaultdict
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("string-utils-ai-mcp")

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
def slugify(text: str, separator: str = "-", max_length: int = 80, lowercase: bool = True, api_key: str = "") -> dict:
    """Convert text to a URL-friendly slug.

    Args:
        text: Text to slugify
        separator: Word separator (default '-')
        max_length: Maximum slug length (default 80)
        lowercase: Convert to lowercase (default True)
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    _check_rate_limit("slugify")
    slug = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    if lowercase:
        slug = slug.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', separator, slug).strip(separator)
    if max_length and len(slug) > max_length:
        slug = slug[:max_length].rstrip(separator)
    return {"slug": slug, "original": text, "length": len(slug)}


@mcp.tool()
def camel_to_snake(text: str, direction: str = "camel_to_snake", api_key: str = "") -> dict:
    """Convert between camelCase, snake_case, kebab-case, and PascalCase.

    Args:
        text: String to convert
        direction: Conversion type - 'camel_to_snake', 'snake_to_camel', 'to_kebab', 'to_pascal', 'to_constant'
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    _check_rate_limit("camel_to_snake")
    # First normalize to words
    words = []
    if '_' in text:
        words = [w for w in text.split('_') if w]
    elif '-' in text:
        words = [w for w in text.split('-') if w]
    else:
        parts = re.sub(r'([A-Z])', r' \1', text).strip().split()
        words = [w.lower() for w in parts if w]
    if not words:
        words = [text.lower()]
    results = {}
    results["snake_case"] = '_'.join(w.lower() for w in words)
    results["camelCase"] = words[0].lower() + ''.join(w.capitalize() for w in words[1:])
    results["PascalCase"] = ''.join(w.capitalize() for w in words)
    results["kebab-case"] = '-'.join(w.lower() for w in words)
    results["CONSTANT_CASE"] = '_'.join(w.upper() for w in words)
    target_map = {"camel_to_snake": "snake_case", "snake_to_camel": "camelCase",
                  "to_kebab": "kebab-case", "to_pascal": "PascalCase", "to_constant": "CONSTANT_CASE"}
    target = target_map.get(direction, "snake_case")
    return {"result": results[target], "direction": direction, "all_formats": results, "words": words}


@mcp.tool()
def truncate_smart(text: str, max_length: int = 100, suffix: str = "...", preserve_words: bool = True, api_key: str = "") -> dict:
    """Smartly truncate text at word boundaries with a suffix.

    Args:
        text: Text to truncate
        max_length: Maximum length including suffix (default 100)
        suffix: Suffix to append when truncated (default '...')
        preserve_words: Don't break mid-word (default True)
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    _check_rate_limit("truncate_smart")
    if len(text) <= max_length:
        return {"text": text, "truncated": False, "original_length": len(text)}
    target_len = max_length - len(suffix)
    if target_len <= 0:
        return {"text": suffix[:max_length], "truncated": True, "original_length": len(text)}
    truncated = text[:target_len]
    if preserve_words and ' ' in truncated:
        last_space = truncated.rfind(' ')
        if last_space > target_len * 0.5:
            truncated = truncated[:last_space]
    truncated = truncated.rstrip(' .,;:!?-')
    result = truncated + suffix
    return {"text": result, "truncated": True, "original_length": len(text),
            "result_length": len(result), "chars_removed": len(text) - len(truncated)}


@mcp.tool()
def extract_numbers(text: str, include_decimals: bool = True, include_negative: bool = True, api_key: str = "") -> dict:
    """Extract all numbers from text.

    Args:
        text: Text to extract numbers from
        include_decimals: Include decimal numbers (default True)
        include_negative: Include negative numbers (default True)
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    _check_rate_limit("extract_numbers")
    if include_negative and include_decimals:
        pattern = r'-?\d+\.?\d*'
    elif include_decimals:
        pattern = r'\d+\.?\d*'
    elif include_negative:
        pattern = r'-?\d+'
    else:
        pattern = r'\d+'
    matches = re.findall(pattern, text)
    numbers = []
    for m in matches:
        try:
            if '.' in m:
                numbers.append(float(m))
            else:
                numbers.append(int(m))
        except ValueError:
            pass
    stats = {}
    if numbers:
        stats = {"min": min(numbers), "max": max(numbers),
                 "sum": sum(numbers), "average": sum(numbers) / len(numbers)}
    return {"numbers": numbers, "count": len(numbers), "statistics": stats}


if __name__ == "__main__":
    mcp.run()
