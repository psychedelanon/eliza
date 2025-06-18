#!/usr/bin/env python3
"""
Simple test for Swarm Quality Boost implementation.
"""

import os
os.environ["DRY_RUN"] = "true"

def test_generator():
    """Test the smart post generator."""
    print("Testing Smart Post Generator...")
    
    try:
        from agents.generator import compose_post
        post = compose_post("LoreMaster", dry_run=True)
        print(f"✅ Generated post: {post}")
        print(f"   Length: {len(post)} chars")
        return True
    except Exception as e:
        print(f"❌ Generator test failed: {e}")
        return False

def test_quality():
    """Test quality validation."""
    print("\nTesting Quality Validation...")
    
    try:
        from agents.quality import validate, get_quality_score
        test_post = "🔮 The ancient scrolls speak of $BITCOIN's rise @LoreMaster #HarryPotterObamaSonic10Inu"
        is_valid, issues = validate(test_post)
        score = get_quality_score(test_post)
        print(f"✅ Quality test passed: valid={is_valid}, score={score:.2f}")
        return True
    except Exception as e:
        print(f"❌ Quality test failed: {e}")
        return False

def test_engagement():
    """Test engagement weights."""
    print("\nTesting Engagement Weights...")
    
    try:
        from agents.generator import get_engagement_weights
        weights = get_engagement_weights("LoreMaster")
        print(f"✅ Engagement weights: {weights}")
        return True
    except Exception as e:
        print(f"❌ Engagement test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Simple Swarm Quality Boost Test")
    print("=" * 40)
    
    tests = [test_generator, test_quality, test_engagement]
    passed = 0
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n{'=' * 40}")
    print(f"Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("✅ All tests passed! Swarm Quality Boost is ready.")
    else:
        print("❌ Some tests failed. Check the implementation.")

if __name__ == "__main__":
    main() 