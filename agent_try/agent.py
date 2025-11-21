"""
Google ADK AI Agent - Professional Implementation

This module provides a production-ready AI agent using Google's Agent Development Kit
with comprehensive error handling, configuration management, and monitoring capabilities.
"""

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search
from google.genai import types
import asyncio
from dotenv import load_dotenv
import os
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass
import logging
from datetime import datetime
import json

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('agent.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class AgentConfig:
    """Configuration for the AI agent with sensible defaults."""
    model_name: str = "gemini-2.5-flash-lite"
    app_name: str = "professional_search_agent"
    user_id: str = "default_user"
    session_id: str = "default_session"
    max_retries: int = 3
    request_timeout: int = 30


class AgentError(Exception):
    """Custom exception for agent-related errors."""
    pass


class ValidationError(AgentError):
    """Raised when input validation fails."""
    pass


class SessionError(AgentError):
    """Raised when session management fails."""
    pass


def load_config() -> AgentConfig:
    """
    Load configuration from environment variables with sensible defaults.
    
    Returns:
        AgentConfig: Configured agent settings
        
    Raises:
        AgentError: If required environment variables are missing
    """
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise AgentError("GOOGLE_API_KEY environment variable is required")
        
        os.environ["GOOGLE_API_KEY"] = api_key
        
        return AgentConfig(
            model_name=os.getenv("MODEL_NAME", "gemini-2.5-flash-lite"),
            app_name=os.getenv("APP_NAME", "professional_search_agent"),
            user_id=os.getenv("USER_ID", "default_user"),
            session_id=os.getenv("SESSION_ID", "default_session"),
            max_retries=int(os.getenv("MAX_RETRIES", "3")),
            request_timeout=int(os.getenv("REQUEST_TIMEOUT", "30"))
        )
    except ValueError as e:
        raise AgentError(f"Invalid configuration value: {e}") from e


def validate_query(query: str) -> None:
    """
    Validate user query before processing.
    
    Args:
        query: User query string to validate
        
    Raises:
        ValidationError: If query fails validation checks
    """
    if not query or not isinstance(query, str):
        raise ValidationError("Query must be a non-empty string")
    
    query = query.strip()
    
    if len(query) == 0:
        raise ValidationError("Query cannot be empty or whitespace only")
    
    if len(query) < 2:
        raise ValidationError("Query too short (minimum 2 characters)")
    
    if len(query) > 2000:
        raise ValidationError("Query too long (maximum 2000 characters)")
    
    # Check for potentially malicious content
    forbidden_patterns = [
        "<script", "javascript:", "onload=", "onerror=",
        "<?php", "eval(", "exec(", "system("
    ]
    
    query_lower = query.lower()
    for pattern in forbidden_patterns:
        if pattern in query_lower:
            raise ValidationError(f"Query contains forbidden pattern: {pattern}")


class SessionManager:
    """
    Manage agent sessions with connection pooling and error handling.
    
    This class provides efficient session management with reuse capabilities
    and proper cleanup of resources.
    """
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.session_service = InMemorySessionService()
        self._sessions: Dict[str, Tuple[Any, Runner]] = {}
        logger.info("SessionManager initialized")
    
    async def get_session_and_runner(self, user_id: str = None, session_id: str = None) -> Tuple[Any, Runner]:
        """
        Get or create session and runner with proper error handling.
        
        Args:
            user_id: Optional user identifier
            session_id: Optional session identifier
            
        Returns:
            Tuple of (session, runner)
            
        Raises:
            SessionError: If session creation fails
        """
        user_id = user_id or self.config.user_id
        session_id = session_id or self.config.session_id
        session_key = f"{user_id}:{session_id}"
        
        try:
            if session_key not in self._sessions:
                logger.debug(f"Creating new session: {session_key}")
                
                # Create session
                session = await self.session_service.create_session(
                    app_name=self.config.app_name,
                    user_id=user_id,
                    session_id=session_id
                )
                
                # Create agent instance for this session
                agent = create_agent(self.config)
                
                # Create runner
                runner = Runner(
                    agent=agent,
                    app_name=self.config.app_name,
                    session_service=self.session_service
                )
                
                self._sessions[session_key] = (session, runner)
                logger.info(f"Created new session and runner: {session_key}")
            else:
                logger.debug(f"Reusing existing session: {session_key}")
            
            return self._sessions[session_key]
            
        except Exception as e:
            logger.error(f"Failed to create session {session_key}: {e}")
            raise SessionError(f"Session creation failed: {e}") from e
    
    def cleanup_session(self, user_id: str = None, session_id: str = None) -> bool:
        """
        Clean up a specific session.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            
        Returns:
            bool: True if session was found and removed
        """
        user_id = user_id or self.config.user_id
        session_id = session_id or self.config.session_id
        session_key = f"{user_id}:{session_id}"
        
        if session_key in self._sessions:
            del self._sessions[session_key]
            logger.info(f"Cleaned up session: {session_key}")
            return True
        
        logger.debug(f"Session not found for cleanup: {session_key}")
        return False
    
    def get_active_sessions_count(self) -> int:
        """Get the number of active sessions."""
        return len(self._sessions)


def create_agent(config: AgentConfig) -> Agent:
    """
    Create and configure the AI agent with professional settings.
    
    Args:
        config: Agent configuration
        
    Returns:
        Agent: Configured Google ADK agent
        
    Raises:
        AgentError: If agent creation fails
    """
    try:
        agent = Agent(
            name="professional_ai_agent",
            model=config.model_name,
            description=(
                "Enterprise-grade AI assistant with web search capabilities. "
                "Provides accurate, helpful, and professional responses."
            ),
            instruction=(
                "You are a helpful, accurate, and professional AI assistant. "
                "Follow these guidelines:\n"
                "1. Provide clear, factual, and well-structured responses\n"
                "2. Use Google Search when needed for current information\n"
                "3. Always cite sources when using web search results\n"
                "4. Be concise but thorough in explanations\n"
                "5. Maintain a professional and helpful tone\n"
                "6. Admit when you don't know something rather than guessing\n"
                "7. For technical questions, provide practical examples when possible"
            ),
            tools=[google_search]
        )
        logger.info(f"Agent created successfully with model: {config.model_name}")
        return agent
    except Exception as e:
        logger.error(f"Failed to create agent: {e}")
        raise AgentError(f"Agent creation failed: {e}") from e


# Global instances
config = load_config()
session_manager = SessionManager(config)
root_agent = create_agent(config)


async def get_agent_response(
    query: str, 
    user_id: str = None, 
    session_id: str = None,
    max_retries: int = None
) -> str:
    """
    Get agent response for a given query with comprehensive error handling and retries.
    
    Args:
        query: The user query string
        user_id: Optional user identifier
        session_id: Optional session identifier
        max_retries: Maximum retry attempts (defaults to config value)
        
    Returns:
        Agent response as string
        
    Raises:
        ValidationError: If query validation fails
        AgentError: If agent processing fails after all retries
    """
    max_retries = max_retries or config.max_retries
    last_exception = None
    
    # Input validation
    validate_query(query)
    
    logger.info(f"Processing query: '{query[:50]}{'...' if len(query) > 50 else ''}'")
    
    for attempt in range(max_retries + 1):
        try:
            # Get session and runner
            session, runner = await session_manager.get_session_and_runner(user_id, session_id)
            
            # Prepare content
            content = types.Content(role='user', parts=[types.Part(text=query)])
            
            # Process query
            events = runner.run_async(
                user_id=user_id or config.user_id,
                session_id=session_id or config.session_id,
                new_message=content
            )

            # Process events and extract response
            async for event in events:
                if event.is_final_response():
                    response_text = event.content.parts[0].text
                    
                    if response_text and response_text.strip():
                        logger.info(
                            f"Successfully generated response for query "
                            f"('{query[:30]}...') - Length: {len(response_text)} chars"
                        )
                        return response_text
                    else:
                        logger.warning(f"Empty response generated for query: '{query}'")
                        return "I apologize, but I couldn't generate a meaningful response. Please try rephrasing your question."
            
            logger.warning(f"No final response event for query: '{query}'")
            return "I apologize, but I couldn't process your request properly. Please try again."
            
        except (ValidationError, SessionError) as e:
            # Don't retry validation or session errors
            logger.error(f"Non-retryable error: {e}")
            raise
        except Exception as e:
            last_exception = e
            logger.warning(
                f"Attempt {attempt + 1}/{max_retries + 1} failed for query "
                f"('{query[:30]}...'): {e}"
            )
            
            if attempt < max_retries:
                # Exponential backoff
                wait_time = 2 ** attempt
                logger.info(f"Retrying in {wait_time} seconds...")
                await asyncio.sleep(wait_time)
            else:
                logger.error(
                    f"All {max_retries + 1} attempts failed for query: '{query}'. "
                    f"Last error: {last_exception}"
                )
                raise AgentError(
                    f"Failed to get agent response after {max_retries + 1} attempts: {last_exception}"
                ) from last_exception
    
    # This should never be reached, but for type safety
    raise AgentError("Unexpected error in get_agent_response")


async def call_agent_async(query: str, user_id: str = None, session_id: str = None) -> None:
    """
    Call agent and print response (legacy function for backward compatibility).
    
    Args:
        query: User query string
        user_id: Optional user identifier
        session_id: Optional session identifier
    """
    try:
        response = await get_agent_response(query, user_id, session_id)
        print(f"🤖 Agent Response: {response}")
    except Exception as e:
        print(f"❌ Error: {e}")


def get_agent_info() -> Dict[str, Any]:
    """
    Get comprehensive information about the configured agent.
    
    Returns:
        Dictionary containing agent configuration and status
    """
    return {
        "agent_name": root_agent.name,
        "model": root_agent.model,
        "description": root_agent.description,
        "available_tools": [tool.__class__.__name__ for tool in root_agent.tools],
        "config": {
            "model_name": config.model_name,
            "app_name": config.app_name,
            "max_retries": config.max_retries,
            "request_timeout": config.request_timeout,
        },
        "session_info": {
            "active_sessions": session_manager.get_active_sessions_count(),
            "default_user_id": config.user_id,
            "default_session_id": config.session_id
        },
        "timestamp": datetime.now().isoformat()
    }


async def health_check() -> Dict[str, Any]:
    """
    Perform comprehensive health check on the agent service.
    
    Returns:
        Dictionary containing health status and metrics
    """
    health_info = {
        "status": "unknown",
        "timestamp": datetime.now().isoformat(),
        "checks": {}
    }
    
    try:
        # Check 1: Basic connectivity
        health_info["checks"]["api_connectivity"] = {
            "status": "checking",
            "message": "Testing Google AI API connectivity"
        }
        
        test_response = await get_agent_response("Hello, are you working?")
        health_info["checks"]["api_connectivity"]["status"] = "healthy"
        health_info["checks"]["api_connectivity"]["message"] = "API connectivity verified"
        health_info["checks"]["api_connectivity"]["response_sample"] = test_response[:100] + "..." if len(test_response) > 100 else test_response
        
        # Check 2: Session management
        health_info["checks"]["session_management"] = {
            "status": "checking",
            "message": "Testing session management"
        }
        
        active_sessions = session_manager.get_active_sessions_count()
        health_info["checks"]["session_management"]["status"] = "healthy"
        health_info["checks"]["session_management"]["message"] = f"Session management working ({active_sessions} active sessions)"
        health_info["checks"]["session_management"]["active_sessions"] = active_sessions
        
        # Check 3: Configuration
        health_info["checks"]["configuration"] = {
            "status": "healthy",
            "message": "Configuration loaded successfully",
            "config": get_agent_info()["config"]
        }
        
        health_info["status"] = "healthy"
        health_info["message"] = "All health checks passed"
        
        logger.info("Health check completed successfully")
        
    except Exception as e:
        health_info["status"] = "unhealthy"
        health_info["message"] = f"Health check failed: {e}"
        health_info["checks"]["api_connectivity"]["status"] = "unhealthy"
        health_info["checks"]["api_connectivity"]["message"] = f"API connectivity test failed: {e}"
        
        logger.error(f"Health check failed: {e}")
    
    return health_info


async def batch_process_queries(queries: list, user_id: str = None, session_id: str = None) -> list:
    """
    Process multiple queries in batch with individual error handling.
    
    Args:
        queries: List of query strings
        user_id: Optional user identifier
        session_id: Optional session identifier
        
    Returns:
        List of results with status for each query
    """
    if not queries:
        raise ValidationError("Queries list cannot be empty")
    
    results = []
    
    for i, query in enumerate(queries, 1):
        try:
            validate_query(query)
            response = await get_agent_response(query, user_id, session_id)
            results.append({
                "query": query,
                "response": response,
                "status": "success",
                "query_id": i
            })
            logger.info(f"Batch processed query {i}/{len(queries)} successfully")
            
        except Exception as e:
            results.append({
                "query": query,
                "response": None,
                "status": "error",
                "error": str(e),
                "query_id": i
            })
            logger.error(f"Batch processing failed for query {i}: {e}")
            
        # Small delay to avoid rate limiting
        if i < len(queries):
            await asyncio.sleep(0.5)
    
    return results


# Demo and testing
async def demo_agent_capabilities():
    """Demonstrate agent capabilities with sample queries."""
    sample_queries = [
        "Hello! Who are you and what can you help me with?",
        "What's the latest news about artificial intelligence?",
        "Explain quantum computing in simple terms",
        "What are the benefits of renewable energy?",
    ]
    
    print("🚀 Demonstrating Agent Capabilities")
    print("=" * 50)
    
    for i, query in enumerate(sample_queries, 1):
        print(f"\n📝 Query {i}: {query}")
        try:
            response = await get_agent_response(query)
            print(f"🤖 Response: {response}\n")
            print("-" * 50)
        except Exception as e:
            print(f"❌ Error: {e}\n")
            print("-" * 50)


if __name__ == "__main__":
    # Run demonstration when script is executed directly
    print("Google ADK AI Agent - Professional Edition")
    print("Loading and testing agent...")
    
    # Test health check first
    async def main():
        health = await health_check()
        print(f"Health Status: {health['status']}")
        
        if health['status'] == 'healthy':
            await demo_agent_capabilities()
        else:
            print("Agent is not healthy. Please check configuration and API key.")
    
    asyncio.run(main())