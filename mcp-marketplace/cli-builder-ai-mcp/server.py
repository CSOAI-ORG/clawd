"""
CLI Builder AI MCP Server
CLI tool generation and parsing utilities powered by MEOK AI Labs.
"""


import sys, os
sys.path.insert(0, os.path.expanduser('~/clawd/meok-labs-engine/shared'))
from auth_middleware import check_access

import re
import time
from collections import defaultdict
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("cli-builder-ai-mcp")

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
def generate_argparse(
    program_name: str, description: str, arguments: list[dict], subcommands: list[dict] | None = None
, api_key: str = "") -> dict:
    """Generate Python argparse CLI boilerplate code.

    Args:
        program_name: CLI program name
        description: Program description
        arguments: List of argument dicts with keys: name, type (str/int/float/bool), help, required (bool), default (optional), choices (list, optional)
        subcommands: Optional list of subcommand dicts with keys: name, help, arguments (same format)
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    _check_rate_limit("generate_argparse")
    lines = ['import argparse', '', '']
    lines.append('def main():')
    lines.append(f'    parser = argparse.ArgumentParser(')
    lines.append(f'        prog="{program_name}",')
    lines.append(f'        description="{description}"')
    lines.append(f'    )')

    def _add_arg(arg, indent="    "):
        name = arg["name"]
        is_positional = not name.startswith("-")
        parts = [f'{indent}parser.add_argument(']
        if is_positional:
            parts.append(f'{indent}    "{name}",')
        else:
            short = f'-{name.lstrip("-")[0]}'
            parts.append(f'{indent}    "{short}", "{name}",')
        atype = arg.get("type", "str")
        if atype == "bool":
            parts.append(f'{indent}    action="store_true",')
        else:
            type_map = {"str": "str", "int": "int", "float": "float"}
            parts.append(f'{indent}    type={type_map.get(atype, "str")},')
        if arg.get("help"):
            parts.append(f'{indent}    help="{arg["help"]}",')
        if arg.get("default") is not None:
            d = arg["default"]
            parts.append(f'{indent}    default={repr(d)},')
        if arg.get("required") and not is_positional:
            parts.append(f'{indent}    required=True,')
        if arg.get("choices"):
            parts.append(f'{indent}    choices={arg["choices"]},')
        parts.append(f'{indent})')
        return parts

    for arg in arguments:
        lines.extend(_add_arg(arg))

    if subcommands:
        lines.append('    subparsers = parser.add_subparsers(dest="command", help="Available commands")')
        for sub in subcommands:
            var = sub["name"].replace("-", "_")
            lines.append(f'    parser_{var} = subparsers.add_parser("{sub["name"]}", help="{sub.get("help", "")}")')
            for arg in sub.get("arguments", []):
                old_lines = _add_arg(arg, "    ")
                for l in old_lines:
                    lines.append(l.replace("parser.add_argument", f"parser_{var}.add_argument"))

    lines.append('    args = parser.parse_args()')
    lines.append('    print(args)')
    lines.append('')
    lines.append('')
    lines.append('if __name__ == "__main__":')
    lines.append('    main()')
    code = '\n'.join(lines)
    return {"code": code, "language": "python", "program_name": program_name,
            "argument_count": len(arguments), "subcommand_count": len(subcommands or [])}


@mcp.tool()
def generate_click(
    program_name: str, description: str, commands: list[dict]
, api_key: str = "") -> dict:
    """Generate Python Click CLI boilerplate code.

    Args:
        program_name: CLI program name
        description: Program description
        commands: List of command dicts with keys: name, help, options (list of dicts with: name, type, help, required, default)
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    _check_rate_limit("generate_click")
    lines = ['import click', '', '']
    lines.append(f'@click.group()')
    lines.append(f'def cli():')
    lines.append(f'    """{description}"""')
    lines.append(f'    pass')
    lines.append('')

    for cmd in commands:
        lines.append(f'@cli.command()')
        for opt in cmd.get("options", []):
            name = opt["name"].lstrip("-")
            otype = opt.get("type", "str")
            type_map = {"str": "str", "int": "int", "float": "float", "bool": "bool"}
            click_type = type_map.get(otype, "str")
            parts = [f'@click.option("--{name}"']
            if click_type == "bool":
                parts[0] = f'@click.option("--{name}/--no-{name}"'
            else:
                parts.append(f'type={click_type}')
            if opt.get("help"):
                parts.append(f'help="{opt["help"]}"')
            if opt.get("required"):
                parts.append('required=True')
            if opt.get("default") is not None:
                parts.append(f'default={repr(opt["default"])}')
            lines.append(', '.join(parts) + ')')
        params = ', '.join(opt["name"].lstrip("-").replace("-", "_") for opt in cmd.get("options", []))
        lines.append(f'def {cmd["name"].replace("-", "_")}({params}):')
        lines.append(f'    """{cmd.get("help", "")}"""')
        lines.append(f'    click.echo(f"Running {cmd["name"]}")')
        lines.append('')

    lines.append('')
    lines.append('if __name__ == "__main__":')
    lines.append('    cli()')
    code = '\n'.join(lines)
    return {"code": code, "language": "python", "program_name": program_name,
            "command_count": len(commands)}


@mcp.tool()
def parse_help_text(help_text: str, api_key: str = "") -> dict:
    """Parse CLI help text output into structured command/option data.

    Args:
        help_text: CLI help text output (e.g., from --help)
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    _check_rate_limit("parse_help_text")
    result = {"program": "", "description": "", "commands": [], "options": [], "positional_args": []}
    lines = help_text.strip().split('\n')
    if lines:
        usage_match = re.match(r'[Uu]sage:\s*(\S+)', lines[0])
        if usage_match:
            result["program"] = usage_match.group(1)
    in_section = None
    for line in lines:
        stripped = line.strip()
        if re.match(r'^(options|optional arguments|flags):', stripped, re.IGNORECASE):
            in_section = "options"
            continue
        elif re.match(r'^(commands|subcommands):', stripped, re.IGNORECASE):
            in_section = "commands"
            continue
        elif re.match(r'^(positional arguments|arguments):', stripped, re.IGNORECASE):
            in_section = "positional"
            continue
        elif stripped and not stripped.startswith('-') and not line.startswith(' ') and in_section is None:
            if not result["description"]:
                result["description"] = stripped
            continue
        if in_section == "options":
            opt_match = re.match(r'\s+(-\w(?:,\s*)?)?(?:\s*(--[\w-]+))?\s*(\S.*)?', line)
            if opt_match:
                short = (opt_match.group(1) or "").strip().rstrip(',')
                long_opt = (opt_match.group(2) or "").strip()
                desc = (opt_match.group(3) or "").strip()
                if short or long_opt:
                    result["options"].append({"short": short, "long": long_opt, "description": desc})
        elif in_section == "commands":
            cmd_match = re.match(r'\s+(\S+)\s+(.*)', line)
            if cmd_match:
                result["commands"].append({"name": cmd_match.group(1), "description": cmd_match.group(2).strip()})
        elif in_section == "positional":
            pos_match = re.match(r'\s+(\S+)\s+(.*)', line)
            if pos_match:
                result["positional_args"].append({"name": pos_match.group(1), "description": pos_match.group(2).strip()})
    return result


@mcp.tool()
def generate_manpage(
    program_name: str, description: str, version: str = "1.0.0",
    synopsis: str = "", options: list[dict] | None = None, examples: list[dict] | None = None,
    author: str = ""
, api_key: str = "") -> dict:
    """Generate a man page in troff format.

    Args:
        program_name: Program name
        description: Program description
        version: Version string
        synopsis: Usage synopsis line
        options: List of option dicts with keys: flag, description
        examples: List of example dicts with keys: command, description
        author: Author name
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    _check_rate_limit("generate_manpage")
    from datetime import date
    today = date.today().strftime("%B %Y")
    name_upper = program_name.upper()
    lines = [
        f'.TH {name_upper} 1 "{today}" "v{version}" "User Commands"',
        '.SH NAME',
        f'{program_name} \\- {description}',
    ]
    if synopsis:
        lines.extend(['.SH SYNOPSIS', f'.B {program_name}', f'{synopsis}'])
    lines.extend(['.SH DESCRIPTION', f'{description}'])
    if options:
        lines.append('.SH OPTIONS')
        for opt in options:
            lines.append(f'.TP')
            lines.append(f'.B {opt["flag"]}')
            lines.append(opt["description"])
    if examples:
        lines.append('.SH EXAMPLES')
        for ex in examples:
            lines.append(f'.TP')
            lines.append(f'.B {ex["command"]}')
            lines.append(ex.get("description", ""))
    if author:
        lines.extend(['.SH AUTHOR', f'Written by {author}.'])
    lines.extend(['.SH VERSION', f'v{version}'])
    manpage = '\n'.join(lines)
    return {"manpage": manpage, "program": program_name, "format": "troff",
            "sections": sum(1 for l in lines if l.startswith('.SH'))}


if __name__ == "__main__":
    mcp.run()
