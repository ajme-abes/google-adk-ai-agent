"""
Performance tests for the Google ADK AI Agent.
"""

import pytest
import asyncio
import time
from agent_try.agent import get_agent_response


class TestAgentPerformance:
    """Performance testing suite for the AI agent."""
    
    def test_single_query_performance(self):
        """Test performance of single query processing."""
        start_time = time.time()
        
        result = asyncio.run(get_agent_response("Hello, how are you?"))
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Performance assertions
        assert total_time < 10.0, f"Query took too long to process: {total_time:.2f}s"
        assert isinstance(result, str), "Response should be a string"
        assert len(result) > 0, "Response should not be empty"
        
        print(f"✅ Single query performance: {total_time:.2f}s")

    def test_batch_processing_performance(self):
        """Test performance of batch query processing."""
        # Use a small batch for performance testing
        test_queries = [
            "What is Python?",
            "Explain machine learning",
            "Tell me a joke"
        ]
        
        start_time = time.time()
        
        # Process queries sequentially
        results = []
        for query in test_queries:
            result = asyncio.run(get_agent_response(query))
            results.append(result)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Performance assertions
        assert total_time < 30.0, f"Batch processing took too long: {total_time:.2f}s"
        
        successful_queries = sum(1 for r in results if r and len(r) > 0)
        success_rate = (successful_queries / len(results)) * 100
        
        assert success_rate >= 80.0, f"Success rate too low: {success_rate}%"
        
        print(f"✅ Batch processing - Total time: {total_time:.2f}s, Success rate: {success_rate:.1f}%")

    def test_response_quality_metrics(self):
        """Test quality metrics of agent responses."""
        test_queries = [
            "What is Python?",
            "Explain machine learning", 
            "Tell me a joke"
        ]
        
        results = []
        for query in test_queries:
            result = asyncio.run(get_agent_response(query))
            results.append(result)
        
        for i, result in enumerate(results):
            # Quality assertions
            assert len(result) > 10, f"Response {i+1} too short: {len(result)} chars"
            assert isinstance(result, str), f"Response {i+1} should be string"
            assert result.strip() != "", f"Response {i+1} should not be empty"
        
        print("✅ All responses meet quality standards")

    def test_concurrent_queries(self):
        """Test handling of concurrent queries."""
        queries = ["Hello"] * 3  # Same query to test concurrency
        
        start_time = time.time()
        
        # Run queries concurrently using asyncio.gather
        async def run_concurrent():
            tasks = [get_agent_response(query) for query in queries]
            return await asyncio.gather(*tasks)
        
        results = asyncio.run(run_concurrent())
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should be faster than sequential processing
        assert total_time < 15.0, f"Concurrent processing took too long: {total_time:.2f}s"
        
        successful = sum(1 for r in results if r and len(r) > 0)
        assert successful >= 2, f"Most concurrent queries should succeed, got {successful}/3"
        
        print(f"✅ Concurrent processing - Total time: {total_time:.2f}s, Successful: {successful}/{len(queries)}")


def test_error_handling_performance():
    """Test performance under error conditions."""
    from agent_try.agent import ValidationError
    import pytest
    
    # Test that invalid queries fail fast
    start_time = time.time()
    
    with pytest.raises(ValidationError):
        asyncio.run(get_agent_response(""))  # Empty query should fail validation
    
    end_time = time.time()
    validation_time = end_time - start_time
    
    # Validation should be very fast
    assert validation_time < 1.0, f"Validation should be fast, took {validation_time:.2f}s"
    
    print(f"✅ Error handling performance: {validation_time:.3f}s")


def test_performance_benchmark():
    """Basic performance benchmark (can be run without async)."""
    # This test can be used for quick performance checks
    assert True
    print("✅ Performance benchmark placeholder passed")


def test_health_check():
    """Test health check functionality."""
    from agent_try.agent import health_check
    
    health = asyncio.run(health_check())
    assert "status" in health
    assert "checks" in health
    assert health["status"] == "healthy"
    
    print("✅ Health check passed")