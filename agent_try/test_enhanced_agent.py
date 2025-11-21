"""
Test script for the enhanced agent.py functionality
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_try.agent import (
    get_agent_response,
    get_agent_info,
    health_check,
    batch_process_queries,
    validate_query,
    AgentError,
    ValidationError
)


async def test_basic_functionality():
    """Test basic agent functionality"""
    print("🧪 Testing Basic Functionality...")
    try:
        response = await get_agent_response("Hello, who are you?")
        print(f"✅ Basic test passed - Response: {response[:100]}...")
        return True
    except Exception as e:
        print(f"❌ Basic test failed: {e}")
        return False


async def test_validation():
    """Test input validation"""
    print("\n🧪 Testing Input Validation...")
    
    # Test valid query
    try:
        validate_query("What is Python?")
        print("✅ Valid query test passed")
    except Exception as e:
        print(f"❌ Valid query test failed: {e}")
        return False
    
    # Test empty query
    try:
        validate_query("")
        print("❌ Empty query test failed - should have raised error")
        return False
    except ValidationError:
        print("✅ Empty query validation passed")
    
    # Test very short query
    try:
        validate_query("a")
        print("❌ Short query test failed - should have raised error")
        return False
    except ValidationError:
        print("✅ Short query validation passed")
    
    return True


async def test_agent_info():
    """Test agent information endpoint"""
    print("\n🧪 Testing Agent Information...")
    try:
        info = get_agent_info()
        print(f"✅ Agent info test passed")
        print(f"   Agent: {info['agent_name']}")
        print(f"   Model: {info['model']}")
        print(f"   Tools: {info['available_tools']}")
        return True
    except Exception as e:
        print(f"❌ Agent info test failed: {e}")
        return False


async def test_health_check():
    """Test health check functionality"""
    print("\n🧪 Testing Health Check...")
    try:
        health = await health_check()
        print(f"✅ Health check test passed - Status: {health['status']}")
        if health['status'] == 'healthy':
            for check_name, check_data in health['checks'].items():
                print(f"   {check_name}: {check_data['status']}")
        return health['status'] == 'healthy'
    except Exception as e:
        print(f"❌ Health check test failed: {e}")
        return False


async def test_batch_processing():
    """Test batch query processing"""
    print("\n🧪 Testing Batch Processing...")
    try:
        queries = [
            "What is machine learning?",
            "Tell me a programming joke",
            "What's the capital of France?"
        ]
        
        results = await batch_process_queries(queries)
        
        success_count = sum(1 for r in results if r['status'] == 'success')
        print(f"✅ Batch processing test passed - {success_count}/{len(queries)} successful")
        
        for result in results:
            status_icon = "✅" if result['status'] == 'success' else "❌"
            print(f"   {status_icon} Query {result['query_id']}: {result['status']}")
            
        return success_count > 0
    except Exception as e:
        print(f"❌ Batch processing test failed: {e}")
        return False


async def test_error_handling():
    """Test error handling capabilities"""
    print("\n🧪 Testing Error Handling...")
    
    # Test with invalid query (should raise ValidationError)
    try:
        await get_agent_response("")
        print("❌ Error handling test failed - should have raised ValidationError")
        return False
    except ValidationError:
        print("✅ Validation error handling passed")
    except Exception as e:
        print(f"❌ Unexpected error type: {e}")
        return False
    
    # Test with very long query (should raise ValidationError)
    try:
        long_query = "x" * 2001  # Exceeds 2000 character limit
        await get_agent_response(long_query)
        print("❌ Long query test failed - should have raised ValidationError")
        return False
    except ValidationError:
        print("✅ Long query validation passed")
    
    return True


async def test_session_management():
    """Test session management functionality"""
    print("\n🧪 Testing Session Management...")
    try:
        # Test with different session IDs
        response1 = await get_agent_response("What is your name?", session_id="test_session_1")
        response2 = await get_agent_response("What is your name?", session_id="test_session_2")
        
        print("✅ Session management test passed - Different sessions created")
        print(f"   Session 1 response: {response1[:50]}...")
        print(f"   Session 2 response: {response2[:50]}...")
        return True
    except Exception as e:
        print(f"❌ Session management test failed: {e}")
        return False


async def run_all_tests():
    """Run all tests and provide summary"""
    print("🚀 Starting Comprehensive Agent Tests")
    print("=" * 60)
    
    tests = [
        ("Basic Functionality", test_basic_functionality),
        ("Input Validation", test_validation),
        ("Agent Information", test_agent_info),
        ("Health Check", test_health_check),
        ("Batch Processing", test_batch_processing),
        ("Error Handling", test_error_handling),
        ("Session Management", test_session_management),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = await test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All tests passed! The enhanced agent is working perfectly!")
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
    
    return passed == total


if __name__ == "__main__":
    # Run the tests
    success = asyncio.run(run_all_tests())
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)