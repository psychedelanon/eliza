#!/usr/bin/env python3
"""
Phase 4 Verification Script

Tests all Phase 4 components to ensure they're working correctly.
Run with: python verify_phase4.py
"""

import sys
import os
import asyncio
from pathlib import Path

def test_imports():
    """Test that all Phase 4 modules can be imported."""
    print("🔍 Testing imports...")
    
    try:
        from eliza.context.store import ContextStore, ContextEntry
        print("  ✅ ContextStore imports OK")
    except Exception as e:
        print(f"  ❌ ContextStore import failed: {e}")
        return False
    
    try:
        from eliza.persona.formatter import render_thread, inject_slang
        print("  ✅ Persona formatter imports OK")
    except Exception as e:
        print(f"  ❌ Persona formatter import failed: {e}")
        return False
    
    try:
        from agents.EnhancedSwarmCoordinator import EnhancedSwarmCoordinator
        print("  ✅ EnhancedSwarmCoordinator imports OK")
    except Exception as e:
        print(f"  ❌ EnhancedSwarmCoordinator import failed: {e}")
        return False
    
    try:
        from agents.base import TwitterAgent
        print("  ✅ TwitterAgent with persona loading imports OK")
    except Exception as e:
        print(f"  ❌ TwitterAgent import failed: {e}")
        return False
    
    return True

def test_persona_templates():
    """Test that persona templates exist and are valid."""
    print("\n🎭 Testing persona templates...")
    
    persona_dir = Path("persona")
    if not persona_dir.exists():
        print(f"  ❌ Persona directory not found: {persona_dir}")
        return False
    
    required_agents = ["agent1", "agent2", "agent3", "agent4", "agent5"]
    
    for agent in required_agents:
        persona_file = persona_dir / f"{agent}.yml"
        if not persona_file.exists():
            print(f"  ❌ Persona file missing: {persona_file}")
            return False
        
        try:
            import yaml
            with open(persona_file, 'r', encoding='utf-8') as f:
                persona = yaml.safe_load(f)
            
            # Check mandatory keys
            required_keys = ["tone", "style_markers", "formats", "argument_chance"]
            for key in required_keys:
                if key not in persona:
                    print(f"  ❌ Missing key '{key}' in {agent}.yml")
                    return False
            
            # Check argument_chance is valid
            arg_chance = persona["argument_chance"]
            if not (0.0 <= arg_chance <= 1.0):
                print(f"  ❌ Invalid argument_chance in {agent}.yml: {arg_chance}")
                return False
            
            print(f"  ✅ {agent}.yml valid")
            
        except Exception as e:
            print(f"  ❌ Error loading {agent}.yml: {e}")
            return False
    
    return True

def test_context_store():
    """Test the ContextStore functionality."""
    print("\n🧠 Testing ContextStore...")
    
    try:
        from eliza.context.store import ContextStore, ContextEntry
        
        # Create test store
        store = ContextStore(max_size=5)
        
        # Test basic push/pull
        store.push("TestAgent", 123, ["crypto_btc", "price_action"])
        store.push("TestAgent2", 124, ["meme_culture"])
        
        recent = store.pull_last(2)
        if len(recent) != 2:
            print(f"  ❌ Expected 2 recent entries, got {len(recent)}")
            return False
        
        # Test last topic
        last_topic = store.last_topic_by_agent("TestAgent")
        if last_topic != "price_action":
            print(f"  ❌ Expected 'price_action', got '{last_topic}'")
            return False
        
        print("  ✅ ContextStore basic functionality works")
        return True
        
    except Exception as e:
        print(f"  ❌ ContextStore test failed: {e}")
        return False

async def main():
    """Run all Phase 4 verification tests."""
    print("🚀 Phase 4 Verification Suite")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports()),
        ("Persona Templates", test_persona_templates()),
        ("ContextStore", test_context_store()),
    ]
    
    passed = 0
    total = len(tests)
    
    print("\n📊 Test Results:")
    for test_name, result in tests:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print("=" * 50)
    print(f"Phase 4 Verification: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Phase 4 is ready!")
        return True
    else:
        print("⚠️  Phase 4 has issues")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 