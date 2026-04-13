"""
Schema Validator AI MCP Server
JSON Schema validation and generation tools powered by MEOK AI Labs.
"""

import json
import time
from collections import defaultdict
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("schema-validator-ai-mcp")

_call_counts: dict[str, list[float]] = defaultdict(list)
FREE_TIER_LIMIT = 50
WINDOW = 86400

TYPE_MAP = {str: "string", int: "integer", float: "number", bool: "boolean", list: "array", dict: "object", type(None): "null"}


def _check_rate_limit(tool_name: str) -> None:
    now = time.time()
    _call_counts[tool_name] = [t for t in _call_counts[tool_name] if now - t < WINDOW]
    if len(_call_counts[tool_name]) >= FREE_TIER_LIMIT:
        raise ValueError(f"Rate limit exceeded for {tool_name}. Free tier: {FREE_TIER_LIMIT}/day. Upgrade at https://meok.ai/pricing")
    _call_counts[tool_name].append(now)


def _infer_type(value) -> dict:
    """Infer JSON Schema type from a Python value."""
    if value is None:
        return {"type": "null"}
    if isinstance(value, bool):
        return {"type": "boolean"}
    if isinstance(value, int):
        return {"type": "integer"}
    if isinstance(value, float):
        return {"type": "number"}
    if isinstance(value, str):
        schema = {"type": "string"}
        if "@" in value and "." in value:
            schema["format"] = "email"
        elif value.startswith("http"):
            schema["format"] = "uri"
        elif len(value) == 10 and value[4:5] == "-":
            schema["format"] = "date"
        return schema
    if isinstance(value, list):
        if value:
            item_types = [_infer_type(v) for v in value[:5]]
            if all(t == item_types[0] for t in item_types):
                return {"type": "array", "items": item_types[0]}
            return {"type": "array", "items": {"anyOf": list({json.dumps(t, sort_keys=True): t for t in item_types}.values())}}
        return {"type": "array"}
    if isinstance(value, dict):
        props = {}
        for k, v in value.items():
            props[k] = _infer_type(v)
        return {"type": "object", "properties": props, "required": list(value.keys())}
    return {}


def _validate_against_schema(data, schema, path="$") -> list:
    """Basic JSON Schema validation without external libs."""
    errors = []
    schema_type = schema.get("type")
    if schema_type:
        actual = TYPE_MAP.get(type(data))
        if isinstance(data, bool) and schema_type != "boolean":
            errors.append({"path": path, "error": f"Expected {schema_type}, got boolean"})
        elif schema_type == "number" and actual in ("integer", "number"):
            pass
        elif actual != schema_type and data is not None:
            errors.append({"path": path, "error": f"Expected {schema_type}, got {actual or type(data).__name__}"})
    if schema_type == "object" and isinstance(data, dict):
        for req in schema.get("required", []):
            if req not in data:
                errors.append({"path": f"{path}.{req}", "error": f"Required property '{req}' missing"})
        for prop, prop_schema in schema.get("properties", {}).items():
            if prop in data:
                errors.extend(_validate_against_schema(data[prop], prop_schema, f"{path}.{prop}"))
    if schema_type == "array" and isinstance(data, list):
        items_schema = schema.get("items", {})
        if items_schema:
            for i, item in enumerate(data):
                errors.extend(_validate_against_schema(item, items_schema, f"{path}[{i}]"))
        if "minItems" in schema and len(data) < schema["minItems"]:
            errors.append({"path": path, "error": f"Array has {len(data)} items, minimum {schema['minItems']}"})
        if "maxItems" in schema and len(data) > schema["maxItems"]:
            errors.append({"path": path, "error": f"Array has {len(data)} items, maximum {schema['maxItems']}"})
    if schema_type == "string" and isinstance(data, str):
        if "minLength" in schema and len(data) < schema["minLength"]:
            errors.append({"path": path, "error": f"String too short: {len(data)} < {schema['minLength']}"})
        if "maxLength" in schema and len(data) > schema["maxLength"]:
            errors.append({"path": path, "error": f"String too long: {len(data)} > {schema['maxLength']}"})
        if "enum" in schema and data not in schema["enum"]:
            errors.append({"path": path, "error": f"Value not in enum: {schema['enum']}"})
    if schema_type in ("integer", "number") and isinstance(data, (int, float)):
        if "minimum" in schema and data < schema["minimum"]:
            errors.append({"path": path, "error": f"Value {data} below minimum {schema['minimum']}"})
        if "maximum" in schema and data > schema["maximum"]:
            errors.append({"path": path, "error": f"Value {data} above maximum {schema['maximum']}"})
    return errors


@mcp.tool()
def validate_json_schema(data_json: str, schema_json: str) -> dict:
    """Validate JSON data against a JSON Schema.

    Args:
        data_json: JSON string of the data to validate
        schema_json: JSON string of the schema to validate against
    """
    _check_rate_limit("validate_json_schema")
    try:
        data = json.loads(data_json)
        schema = json.loads(schema_json)
    except json.JSONDecodeError as e:
        return {"valid": False, "error": f"JSON parse error: {e}"}
    errors = _validate_against_schema(data, schema)
    return {"valid": len(errors) == 0, "errors": errors, "error_count": len(errors)}


@mcp.tool()
def generate_schema(data_json: str, title: str = "") -> dict:
    """Generate a JSON Schema from example JSON data.

    Args:
        data_json: Example JSON data string
        title: Optional schema title
    """
    _check_rate_limit("generate_schema")
    try:
        data = json.loads(data_json)
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON: {e}"}
    schema = {"$schema": "https://json-schema.org/draft/2020-12/schema"}
    if title:
        schema["title"] = title
    schema.update(_infer_type(data))
    return {"schema": json.dumps(schema, indent=2), "schema_object": schema}


@mcp.tool()
def convert_openapi(openapi_json: str, extract_schemas: bool = True) -> dict:
    """Extract and convert schemas from an OpenAPI specification.

    Args:
        openapi_json: OpenAPI spec as JSON string
        extract_schemas: Whether to extract component schemas (default True)
    """
    _check_rate_limit("convert_openapi")
    try:
        spec = json.loads(openapi_json)
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON: {e}"}
    info = spec.get("info", {})
    paths = spec.get("paths", {})
    endpoints = []
    for path, methods in paths.items():
        for method, details in methods.items():
            if method in ("get", "post", "put", "delete", "patch"):
                endpoints.append({"path": path, "method": method.upper(),
                                  "summary": details.get("summary", ""), "operationId": details.get("operationId", "")})
    schemas = {}
    if extract_schemas:
        components = spec.get("components", {}).get("schemas", {})
        for name, schema in components.items():
            schemas[name] = schema
    return {"title": info.get("title", ""), "version": info.get("version", ""),
            "endpoints": endpoints, "endpoint_count": len(endpoints),
            "schemas": schemas, "schema_count": len(schemas)}


@mcp.tool()
def validate_types(data_json: str, type_spec: dict) -> dict:
    """Validate that JSON data fields match expected types.

    Args:
        data_json: JSON string to validate
        type_spec: Dict mapping field paths to expected types (e.g., {"name": "string", "age": "integer"})
    """
    _check_rate_limit("validate_types")
    try:
        data = json.loads(data_json)
    except json.JSONDecodeError as e:
        return {"valid": False, "error": f"Invalid JSON: {e}"}
    errors = []
    for field, expected_type in type_spec.items():
        parts = field.split('.')
        value = data
        found = True
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                errors.append({"field": field, "error": "Field not found"})
                found = False
                break
        if found:
            actual = TYPE_MAP.get(type(value), type(value).__name__)
            if expected_type == "number" and actual in ("integer", "number"):
                continue
            if actual != expected_type:
                errors.append({"field": field, "expected": expected_type, "actual": actual})
    return {"valid": len(errors) == 0, "errors": errors, "fields_checked": len(type_spec)}


if __name__ == "__main__":
    mcp.run()
