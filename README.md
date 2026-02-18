# STORMer

STORM (Structured Thoughts Outlining Research Methodology) implementation using PydanticAI.

## Installation

```bash
uv sync
```

## Configuration

Copy `.env.example` to `.env` and add your API keys:

```bash
cp .env.example .env
```

Required environment variables:
- `OPENROUTER_API_KEY`: Get from https://openrouter.ai/keys
- `TAVILY_API_KEY`: Get from https://tavily.com/

## Running Tests

```bash
uv run pytest
```

## Development

```bash
# Run linting
uv run ruff check .

# Format code
uv run ruff format .
```
