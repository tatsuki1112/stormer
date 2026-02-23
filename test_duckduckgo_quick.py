"""Quick test script for DuckDuckGo connectivity check.

This script demonstrates that DuckDuckGo works without any API key.
"""

import asyncio
from stormer.connectivity import DuckDuckGoHealthChecker


async def main():
    """Test DuckDuckGo connectivity."""
    print("Testing DuckDuckGo connectivity (no API key required)...\n")

    # Create a DuckDuckGo health checker
    # Note: No API key needed!
    checker = DuckDuckGoHealthChecker(timeout=10.0)

    try:
        result = await checker.check_health()

        print(f"Status: {result.status.value}")
        print(f"Message: {result.message}")
        if result.response_time_ms:
            print(f"Response time: {result.response_time_ms:.2f}ms")
        if result.details:
            print(f"Results found: {result.details.get('result_count', 0)}")

        print("\n✅ DuckDuckGo connectivity check successful!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
