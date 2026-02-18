# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Automating the pre-writing stage to create structured outlines and comprehensive articles using diverse research perspectives.
## Build & Run Commands

This project uses `uv` for Python package management.


## Architecture

Reference: Please refer to storm.md, which contains the summarized essence and core logic of the STORM paper.

### Tech Stack & Core Technologies
Framework: Use PydanticAI for building the agentic workflow.

LLM API: Use OpenRouter as the primary interface for language models.

Search API: Use Tavily for high-quality, research-oriented web searching.

## Development Workflow (TDD Required)

**All feature development and bug fixes MUST follow Test-Driven Development:**

### TDD Cycle (Red-Green-Refactor)

1. **RED** - Write a failing test first
   - Create test file in `tests/` if it doesn't exist
   - Write test that defines expected behavior
   - Run `uv run pytest tests/test_<module>.py -v` to confirm it fails

2. **GREEN** - Write minimal code to pass the test
   - Implement only enough code to make the test pass
   - Run tests again to confirm they pass

3. **REFACTOR** - Clean up while keeping tests green
   - Improve code structure without changing behavior
   - Ensure all tests still pass after refactoring

### Mandatory Practices

- **Never write implementation code without a failing test first**
- **Run tests after every change** to verify behavior
- **Test file naming**: `tests/test_<module_name>.py`
- **Test function naming**: `test_<behavior_being_tested>`
- **One assertion per test** when practical for clear failure messages


