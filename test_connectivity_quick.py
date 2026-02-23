"""Quick test script for connectivity checking."""

import asyncio
import sys
from stormer.config import get_config
from stormer.connectivity.exceptions import ConnectivityCheckError


async def test_connectivity():
    """Test connectivity for both services."""
    config = get_config()

    results = {
        "openrouter": None,
        "tavily": None,
    }

    # Test OpenRouter
    print("Testing OpenRouter...")
    try:
        checker = config.create_openrouter_checker()
        result = await checker.check_health()
        results["openrouter"] = result
        print(f"  ✅ {result.status.value}: {result.message}")
        if result.response_time_ms:
            print(f"  ⏱️  Response time: {result.response_time_ms:.2f}ms")
        if result.details:
            print(f"  📊 {result.details}")
    except ConnectivityCheckError as e:
        print(f"  ❌ Error: {e}")
        results["openrouter"] = str(e)

    print()

    # Test Tavily
    print("Testing Tavily...")
    try:
        checker = config.create_tavily_checker()
        result = await checker.check_health()
        results["tavily"] = result
        print(f"  ✅ {result.status.value}: {result.message}")
        if result.response_time_ms:
            print(f"  ⏱️  Response time: {result.response_time_ms:.2f}ms")
        if result.details:
            print(f"  📊 {result.details}")
    except ConnectivityCheckError as e:
        print(f"  ❌ Error: {e}")
        results["tavily"] = str(e)

    print()
    print("=" * 50)
    print("SUMMARY")
    print("=" * 50)

    # Exit with error code if any service failed
    openrouter_ok = isinstance(results["openrouter"], object) and hasattr(results["openrouter"], 'status')
    tavily_ok = isinstance(results["tavily"], object) and hasattr(results["tavily"], 'status')

    if openrouter_ok and tavily_ok:
        print("✅ All services are operational!")
        return 0
    else:
        print("❌ Some services have issues:")
        if not openrouter_ok:
            print(f"  - OpenRouter: {results['openrouter']}")
        if not tavily_ok:
            print(f"  - Tavily: {results['tavily']}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(test_connectivity())
    sys.exit(exit_code)
