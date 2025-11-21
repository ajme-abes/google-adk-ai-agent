"""
Professional Agent Runner for Google ADK AI Agent.

This module provides a robust, production-ready agent runner with advanced
features like batch processing, performance tracking, and error handling.
"""

import asyncio
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import logging
from dataclasses import dataclass
from google.genai import types

from agent_try.agent import get_agent_response, session_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class AgentResponse:
    """Structured response from the agent."""
    query: str
    response: str
    processing_time: float
    timestamp: datetime
    success: bool
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class AgentRunner:
    """
    A professional agent runner with advanced features for production use.
    
    Features:
    - Batch query processing
    - Performance metrics
    - Error handling and retries
    - Structured logging
    - Response validation
    """
    
    def __init__(self, agent_name: str = "professional_ai_agent"):
        self.agent_name = agent_name
        self.session_service = None
        self.runner = None
        self.metrics = {
            "total_queries": 0,
            "successful_queries": 0,
            "failed_queries": 0,
            "total_processing_time": 0.0
        }
        
    async def initialize(self) -> bool:
        try:
            # Use the global session_manager instead of creating our own
            from agent_try.agent import session_manager
            self.session_manager = session_manager
        
            # Test that we can create a session
            session, runner = await self.session_manager.get_session_and_runner()
            self.session_service = runner.session_service
            self.runner = runner
        
            logger.info(f"Agent '{self.agent_name}' initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize agent: {e}")
            return False
    
    async def run_query(self, query: str, query_id: int = None, 
                       max_retries: int = 2) -> AgentResponse:
        """
        Run a single query through the agent with comprehensive logging and retries.
        
        Args:
            query: The user query to process
            query_id: Optional ID for tracking multiple queries
            max_retries: Number of retry attempts on failure
            
        Returns:
            Structured AgentResponse object
        """
        start_time = time.time()
        
        for attempt in range(max_retries + 1):
            try:
                logger.info(f"Processing query {query_id}: '{query[:50]}...'")
                
                # Get agent response using the helper function
                response_text = await get_agent_response(query)
                
                end_time = time.time()
                processing_time = end_time - start_time
                
                # Validate response
                if not response_text or not response_text.strip():
                    raise ValueError("Empty response from agent")
                
                self.metrics["total_queries"] += 1
                self.metrics["successful_queries"] += 1
                self.metrics["total_processing_time"] += processing_time
                
                return AgentResponse(
                    query=query,
                    response=response_text,
                    processing_time=processing_time,
                    timestamp=datetime.now(),
                    success=True,
                    metadata={
                        "query_id": query_id,
                        "attempts": attempt + 1,
                        "response_length": len(response_text)
                    }
                )
                
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed for query {query_id}: {e}")
                
                if attempt == max_retries:
                    end_time = time.time()
                    processing_time = end_time - start_time
                    
                    self.metrics["total_queries"] += 1
                    self.metrics["failed_queries"] += 1
                    
                    return AgentResponse(
                        query=query,
                        response="",
                        processing_time=processing_time,
                        timestamp=datetime.now(),
                        success=False,
                        error=str(e),
                        metadata={
                            "query_id": query_id,
                            "attempts": attempt + 1
                        }
                    )
                
                # Wait before retry
                await asyncio.sleep(1)
    
    async def run_batch_queries(self, queries: List[str], 
                              batch_size: int = 5) -> List[AgentResponse]:
        """
        Run multiple queries in controlled batches.
        
        Args:
            queries: List of queries to process
            batch_size: Number of queries to process concurrently
            
        Returns:
            List of AgentResponse objects
        """
        logger.info(f"Starting batch processing of {len(queries)} queries")
        
        results = []
        total_start_time = time.time()
        
        # Process in batches to avoid overwhelming the API
        for i in range(0, len(queries), batch_size):
            batch = queries[i:i + batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}/{(len(queries)-1)//batch_size + 1}")
            
            batch_tasks = []
            for j, query in enumerate(batch, 1):
                query_id = i + j
                task = self.run_query(query, query_id=query_id)
                batch_tasks.append(task)
            
            # Process batch concurrently
            batch_results = await asyncio.gather(*batch_tasks)
            results.extend(batch_results)
            
            # Small delay between batches
            if i + batch_size < len(queries):
                await asyncio.sleep(2)
        
        total_end_time = time.time()
        total_time = total_end_time - total_start_time
        
        self._print_batch_summary(results, total_time)
        return results
    
    def _print_batch_summary(self, results: List[AgentResponse], total_time: float):
        """Print a comprehensive batch processing summary."""
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        avg_time = total_time / len(results) if results else 0
        
        print(f"\n{'='*60}")
        print("📊 BATCH PROCESSING SUMMARY")
        print(f"{'='*60}")
        print(f"Total queries processed: {len(results)}")
        print(f"✅ Successful responses: {successful}")
        print(f"❌ Failed responses: {failed}")
        print(f"⏱️ Total processing time: {total_time:.2f}s")
        print(f"📈 Average time per query: {avg_time:.2f}s")
        print(f"🎯 Success rate: {(successful/len(results))*100:.1f}%")
        
        # Performance metrics
        if successful > 0:
            avg_response_time = self.metrics["total_processing_time"] / successful
            print(f"⚡ Average response time: {avg_response_time:.2f}s")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics."""
        metrics = self.metrics.copy()
        if metrics["total_queries"] > 0:
            metrics["success_rate"] = (metrics["successful_queries"] / metrics["total_queries"]) * 100
            metrics["average_processing_time"] = (
                metrics["total_processing_time"] / metrics["total_queries"]
            )
        return metrics
    
    def save_results_to_file(self, results: List[AgentResponse], filename: str = "agent_results.json"):
        """Save results to a JSON file for analysis."""
        output_data = {
            "timestamp": datetime.now().isoformat(),
            "metrics": self.get_performance_metrics(),
            "results": [
                {
                    "query": r.query,
                    "response": r.response,
                    "processing_time": r.processing_time,
                    "success": r.success,
                    "error": r.error,
                    "metadata": r.metadata
                }
                for r in results
            ]
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"Results saved to {filename}")


def get_sample_queries() -> List[str]:
    """Return a curated list of sample queries for testing."""
    return [
        "Hello! Who are you and what can you help me with?",
        "Tell me a funny programming joke.",
        "What's the capital of France and one interesting fact about it?",
        "Give me a brief summary of Python programming language.",
        "What are the benefits of using AI agents?",
        "Explain quantum computing in simple terms.",
        "What's the weather like today?",
        "Who won the latest Nobel Prize in Physics?",
    ]


def get_creative_queries() -> List[str]:
    """Return more creative and challenging queries."""
    return [
        "Write a short haiku about artificial intelligence",
        "If you were a superhero, what would your power be and why?",
        "Describe the future of human-computer interaction in 2050",
        "What's the most interesting scientific discovery of the past decade?",
        "Create a recipe for a dish that represents machine learning",
    ]


async def interactive_mode(runner: AgentRunner):
    """Run the agent in interactive mode for real-time queries."""
    print("\n🎮 INTERACTIVE MODE")
    print("Type your questions (or 'quit' to exit):")
    
    query_count = 0
    
    while True:
        try:
            query = input("\n🤔 You: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
                
            if not query:
                continue
            
            query_count += 1
            result = await runner.run_query(query, query_id=query_count)
            
            if result.success:
                print(f"🤖 Agent: {result.response}")
                print(f"⏱️ Time: {result.processing_time:.2f}s")
            else:
                print(f"❌ Error: {result.error}")
            
        except KeyboardInterrupt:
            print("\n👋 Interrupted by user. Goodbye!")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")