# Human Reliability Program MCP Server

A FastMCP-based Model Context Protocol server for querying DOE Human Reliability Program (10 CFR Part 712) regulations.

## Overview

This MCP server provides AI assistants with tools to search and retrieve information from 10 CFR Part 712 - the federal regulation governing the Human Reliability Program (HRP) for DOE and NNSA facilities.

## Features

- Semantic search across 10 CFR Part 712
- Section and subpart retrieval
- HRP terminology definitions (712.3)
- Certification requirements lookup
- Medical standards (Subpart B)
- Drug/alcohol testing requirements
- Removal, reinstatement, and appeal procedures

## Quick Start

```bash
# Create virtual environment
python3.10 -m venv .venv
source .venv/bin/activate

# Install
pip install -e .

# Run server
python -m hrp_mcp.server
```

## Docker

```bash
docker-compose up -d
```

## Documentation

See [CLAUDE.md](CLAUDE.md) for full documentation.

## Data Source

Regulations are sourced from the public [eCFR](https://www.ecfr.gov/current/title-10/chapter-III/part-712).

## Author

Michael K Alber ([@michaelalber](https://github.com/michaelalber))

## License

Apache License 2.0 - see [LICENSE](LICENSE)
