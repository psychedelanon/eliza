#!/usr/bin/env python3
"""
Test to verify the shared memory fix works.
"""

import os
os.environ["DRY_RUN"] = "true"

def test_shared_memory():
    """Test shared memory functionality."""
    print("Testing Shared Memory...")
    
    try:
        from eliza import shared_memory
        mem = shared_memory.get_shared_memory()
        print(f"✅ Shared memory instance: {type(mem)}")
        
        # Test publishing an event
        event = {"type": "test", "data": "test_value"}
        mem.publish_event(event)
        print("✅ Event published successfully")
        
        # Test getting latest event
        latest_event = mem.get_latest_event()
        print(f"✅ Latest event: {latest_event}")
        
        return True
    except Exception as e:
        print(f"❌ Shared memory test failed: {e}")
        return False

def test_persona_agent():
    """Test persona agent with fixed shared memory."""
    print("\nTesting Persona Agent...")
    
    try:
        from agents.personas import LoreMaster
        agent = LoreMaster(name="LoreMaster", personality="lore", dry_run=True)
        print(f"✅ Agent created: {agent.name}")
        
        # Test craft_post method
        import asyncio
        post = asyncio.run(agent.craft_post())
        print(f"✅ Generated post: {post}")
        print(f"   Length: {len(post)} chars")
        
        return True
    except Exception as e:
        print(f"❌ Persona agent test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("🧪 Testing Shared Memory Fix")
    print("=" * 40)
    
    tests = [test_shared_memory, test_persona_agent]
    passed = 0
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n{'=' * 40}")
    print(f"Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("✅ All tests passed! Shared memory fix is working.")
    else:
        print("❌ Some tests failed. Check the implementation.")

if __name__ == "__main__":
    main() 