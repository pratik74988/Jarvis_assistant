#!/usr/bin/env python3
"""
Test script for screenshot functionality integration
"""

from brain import get_response
from memory import add_to_history, get_context

def test_screenshot_integration():
    """Test the screenshot functionality"""
    print("Testing screenshot integration...")
    
    # Test 1: Basic screenshot command
    print("\n1. Testing basic screenshot command...")
    test_input = "take a screenshot"
    response = get_response(test_input, get_context())
    print(f"Input: {test_input}")
    print(f"Response: {response}")
    
    # Test 2: Screenshot with question
    print("\n2. Testing screenshot with question...")
    test_input = "what do you see on my screen?"
    response = get_response(test_input, get_context())
    print(f"Input: {test_input}")
    print(f"Response: {response}")
    
    # Test 3: Regular conversation (should not trigger screenshot)
    print("\n3. Testing regular conversation...")
    test_input = "hello jarvis, how are you?"
    response = get_response(test_input, get_context())
    print(f"Input: {test_input}")
    print(f"Response: {response}")

if __name__ == "__main__":
    test_screenshot_integration()


