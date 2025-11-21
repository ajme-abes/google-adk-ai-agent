# 📚 API Reference

## AgentRunner Class

The main class for interacting with the Google ADK AI Agent.

### Constructor
```python
AgentRunner(agent_name: str = "professional_ai_agent")
```

**Parameters**:
- `agent_name`: Descriptive name for the agent instance (default: "professional_ai_agent")

### Methods

#### `initialize() -> bool`
Initializes the agent session and runner.

**Returns**: 
- `bool` - True if initialization successful, False otherwise

**Raises**:
- `ConnectionError`: If unable to connect to Google AI services
- `AuthenticationError`: If API key is invalid or missing
- `RuntimeError`: If agent configuration is invalid

#### `run_query(query: str, query_id: Optional[int] = None, max_retries: int = 2) -> AgentResponse`
Process a single query through the agent with comprehensive error handling and retry logic.

**Parameters**:
- `query`: User query string (required, must not be empty)
- `query_id`: Optional numeric identifier for tracking multiple queries
- `max_retries`: Number of retry attempts on API failures (default: 2, max: 5)

**Returns**: 
- `AgentResponse` object containing:
  - Response text
  - Processing metrics
  - Success status
  - Error information (if any)

**Raises**:
- `ValueError`: If query is empty or None
- `TimeoutError`: If request times out after all retries
- `APIError`: If Google API returns an error

#### `run_batch_queries(queries: List[str], batch_size: int = 5) -> List[AgentResponse]`
Process multiple queries in controlled batches with concurrent processing.

**Parameters**:
- `queries`: List of query strings (required, must not be empty)
- `batch_size`: Number of concurrent queries (default: 5, max: 10)

**Returns**: 
- `List[AgentResponse]` - List of response objects in the same order as input queries

**Raises**:
- `ValueError`: If queries list is empty
- `RuntimeError`: If batch processing fails

#### `get_performance_metrics() -> Dict[str, Any]`
Get comprehensive performance metrics for monitoring and analytics.

**Returns**: 
- `Dict[str, Any]` with performance data including:
  - `total_queries`: Total queries processed
  - `successful_queries`: Number of successful responses
  - `failed_queries`: Number of failed responses
  - `success_rate`: Percentage of successful queries
  - `average_processing_time`: Average time per query in seconds
  - `total_processing_time`: Cumulative processing time

#### `save_results_to_file(results: List[AgentResponse], filename: str) -> None`
Save processing results to JSON file for analysis and reporting.

**Parameters**:
- `results`: List of AgentResponse objects to save
- `filename`: Output filename (will be created if doesn't exist)

**Raises**:
- `IOError`: If file cannot be written
- `PermissionError`: If no write access to directory

## AgentResponse Dataclass

Structured response container with comprehensive metadata.

**Attributes**:
- `query: str` - Original query text
- `response: str` - Agent response text (empty if failed)
- `processing_time: float` - Time taken in seconds
- `timestamp: datetime` - When query was processed
- `success: bool` - Whether query succeeded
- `error: Optional[str]` - Error message if failed
- `metadata: Dict[str, Any]` - Additional processing data including:
  - `query_id`: Query identifier
  - `attempts`: Number of attempts made
  - `response_length`: Length of response text
  - `model_used`: AI model used for generation

## Utility Functions

### `get_sample_queries() -> List[str]`
Returns a curated list of sample queries for testing and demonstration.

**Returns**:
- `List[str]` - 8 diverse sample queries covering different topics

### `get_creative_queries() -> List[str]`
Returns creative and open-ended queries for testing advanced capabilities.

**Returns**:
- `List[str]` - 5 creative queries requiring imaginative responses

### `interactive_mode(runner: AgentRunner) -> None`
Starts an interactive command-line interface for real-time conversations.

**Parameters**:
- `runner`: Initialized AgentRunner instance

**Features**:
- Real-time query processing
- Conversation history
- Exit commands ('quit', 'exit', 'q')
- Error handling and user-friendly messages

## Example Usage

### Basic Usage
```python
from agent_try.agent_runner import AgentRunner

async def demo():
    runner = AgentRunner()
    await runner.initialize()
    
    # Single query
    result = await runner.run_query("Hello world!")
    
    # Batch processing
    queries = ["Query 1", "Query 2"]
    results = await runner.run_batch_queries(queries)
    
    # Get metrics
    metrics = runner.get_performance_metrics()
```

### Advanced Usage with Error Handling
```python
from agent_try.agent_runner import AgentRunner

async def robust_demo():
    runner = AgentRunner()
    
    try:
        if not await runner.initialize():
            print("Failed to initialize agent")
            return
            
        # Single query with comprehensive error handling
        result = await runner.run_query("Complex query", query_id=1, max_retries=3)
        
        if result.success:
            print(f"✅ Response: {result.response}")
            print(f"⏱️ Processing time: {result.processing_time:.2f}s")
        else:
            print(f"❌ Error: {result.error}")
            
    except ValueError as e:
        print(f"Invalid input: {e}")
    except TimeoutError as e:
        print(f"Request timed out: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
```

### Batch Processing with Analysis
```python
from agent_try.agent_runner import AgentRunner, get_sample_queries

async def batch_analysis():
    runner = AgentRunner()
    await runner.initialize()
    
    queries = get_sample_queries()
    results = await runner.run_batch_queries(queries, batch_size=3)
    
    # Analyze results
    successful = [r for r in results if r.success]
    failed = [r for r in results if not r.success]
    
    print(f"Processed {len(queries)} queries")
    print(f"Success rate: {(len(successful)/len(queries))*100:.1f}%")
    
    # Save results for later analysis
    runner.save_results_to_file(results, "batch_results.json")
```

## Error Handling

### Structured Error Information
The API provides comprehensive error information through multiple channels:

```python
# Method 1: Check success flag
result = await runner.run_query("test")
if not result.success:
    print(f"Query failed: {result.error}")

# Method 2: Exception handling
try:
    result = await runner.run_query("")
except ValueError as e:
    print(f"Validation error: {e}")

# Method 3: Batch error analysis
results = await runner.run_batch_queries(queries)
for i, result in enumerate(results):
    if not result.success:
        print(f"Query {i+1} failed: {result.error}")
```

### Common Error Types
- **Validation Errors**: Invalid input parameters
- **API Errors**: Google AI service failures
- **Network Errors**: Connection timeouts and interruptions
- **Processing Errors**: Response generation failures

## Performance Metrics

### Available Metrics
- **Total queries processed**: Cumulative count of all queries
- **Success rate**: Percentage of successful responses
- **Average processing time**: Mean time per query in seconds
- **Error distribution**: Breakdown of error types and frequencies
- **Throughput**: Queries processed per minute

### Monitoring Example
```python
metrics = runner.get_performance_metrics()
print(f"Success Rate: {metrics['success_rate']:.1f}%")
print(f"Average Time: {metrics['average_processing_time']:.2f}s")
print(f"Total Processed: {metrics['total_queries']}")
```

## Configuration

### Environment Variables
- `GOOGLE_API_KEY`: Your Google AI API key (required)
- `MODEL_NAME`: Gemini model name (default: "gemini-2.5-flash-lite")
- `APP_NAME`: Application identifier (default: "google_search_agent")
- `MAX_RETRIES`: Maximum retry attempts (default: 2)

### Best Practices
1. Always initialize the agent before use
2. Use appropriate batch sizes for your use case
3. Implement proper error handling for production use
4. Monitor performance metrics for optimization
5. Save important results for analysis and debugging
