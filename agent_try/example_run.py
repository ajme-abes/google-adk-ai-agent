"""
Example script for running the Google ADK agent with multiple queries.

This script demonstrates how to interact with the agent using various queries
and handles different types of responses and errors.
"""

import asyncio
import time
from typing import List, Dict, Any
from datetime import datetime
from agent_try.agent import root_agent, get_agent_response, setup_session_and_runner
from google.genai import types
import os


class AgentRunner:
    """A professional agent runner with logging, timing, and error handling."""
    
    def __init__(self, agent_name: str = "basic_search_agent"):
        self.agent_name = agent_name
        self.session_service = None
        self.runner = None
        
    async def initialize(self):
        """Initialize the agent session and runner."""
        try:
            from agent_try.agent import setup_session_and_runner
            session, runner = await setup_session_and_runner()
            self.session_service = runner.session_service
            self.runner = runner
            print(f"✅ Agent '{self.agent_name}' initialized successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize agent: {e}")
            return False
    
    async def run_query(self, query: str, query_id: int = None) -> Dict[str, Any]:
        """
        Run a single query through the agent with comprehensive logging.
        
        Args:
            query: The user query to process
            query_id: Optional ID for tracking multiple queries
            
        Returns:
            Dictionary containing response data and metadata
        """
        start_time = time.time()
        
        try:
            print(f"\n{'='*60}")
            if query_id:
                print(f"QUERY #{query_id}: {query}")
            else:
                print(f"QUERY: {query}")
            print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*60}")
            
            # Get agent response using the helper function
            response = await get_agent_response(query)
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            result = {
                "query": query,
                "response": response,
                "processing_time": processing_time,
                "timestamp": datetime.now(),
                "success": True,
                "error": None
            }
            
            print(f"🔄 Processing time: {processing_time:.2f}s")
            print(f"📝 Response: {response}")
            
            return result
            
        except Exception as e:
            end_time = time.time()
            processing_time = end_time - start_time
            
            result = {
                "query": query,
                "response": None,
                "processing_time": processing_time,
                "timestamp": datetime.now(),
                "success": False,
                "error": str(e)
            }
            
            print(f"❌ Error after {processing_time:.2f}s: {e}")
            return result
    
    async def run_batch_queries(self, queries: List[str]) -> List[Dict[str, Any]]:
        """
        Run multiple queries in sequence and collect results.
        
        Args:
            queries: List of queries to process
            
        Returns:
            List of result dictionaries for each query
        """
        print(f"\n🎯 Starting batch processing of {len(queries)} queries")
        print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        results = []
        total_start_time = time.time()
        
        for i, query in enumerate(queries, 1):
            result = await self.run_query(query, query_id=i)
            results.append(result)
            
            # Small delay between queries to be respectful of API limits
            if i < len(queries):
                await asyncio.sleep(1)
        
        total_end_time = time.time()
        total_time = total_end_time - total_start_time
        
        # Generate summary
        successful = sum(1 for r in results if r['success'])
        failed = len(queries) - successful
        avg_time = total_time / len(queries)
        
        print(f"\n{'='*60}")
        print("📊 BATCH PROCESSING SUMMARY")
        print(f"{'='*60}")
        print(f"Total queries: {len(queries)}")
        print(f"✅ Successful: {successful}")
        print(f"❌ Failed: {failed}")
        print(f"⏱️ Total time: {total_time:.2f}s")
        print(f"📈 Average time per query: {avg_time:.2f}s")
        print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return results


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
    
    while True:
        try:
            query = input("\n🤔 You: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
                
            if not query:
                continue
                
            await runner.run_query(query)
            
        except KeyboardInterrupt:
            print("\n👋 Interrupted by user. Goodbye!")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")


async def main():
    """Main function to demonstrate agent capabilities."""
    print("🚀 Google ADK Agent Demo")
    print("=" * 50)
    
    # Initialize the agent runner
    runner = AgentRunner()
    if not await runner.initialize():
        return
    
    # Choose mode
    print("\nSelect mode:")
    print("1. Batch mode (predefined queries)")
    print("2. Creative batch mode")
    print("3. Interactive mode (type your own queries)")
    
    try:
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == "1":
            queries = get_sample_queries()
            await runner.run_batch_queries(queries)
            
        elif choice == "2":
            queries = get_creative_queries()
            await runner.run_batch_queries(queries)
            
        elif choice == "3":
            await interactive_mode(runner)
            
        else:
            print("❌ Invalid choice. Running sample batch mode.")
            queries = get_sample_queries()
            await runner.run_batch_queries(queries)
            
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user.")
    except Exception as e:
        print(f"❌ Demo failed: {e}")


if __name__ == "__main__":
    # Set event loop policy for Windows if needed
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    # Run the main function
    asyncio.run(main())