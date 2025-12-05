# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

twpm is a workflow builder library that simplifies creating dynamic workflows using a linked-list-based execution model. The project combines data structure implementations (for learning) with a workflow orchestration system.

## Common Development Commands

This project uses **uv** for Python package management. uv is a fast Python package installer and resolver written in Rust.

### Setup
```bash
# Install dependencies (including dev dependencies)
uv sync

# Install only production dependencies
uv sync --no-dev
```

### Testing
```bash
# Run all tests
uv run pytest

# Run tests with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/core/test_orchestrator.py

# Run single test
uv run pytest tests/core/test_orchestrator.py::TestOrchestrator::test_single_node_execution
```

### Linting and Formatting
```bash
# Check code with ruff (linter)
uv run ruff check .

# Auto-fix linting issues
uv run ruff check --fix .

# Format code with ruff
uv run ruff format .

# Check formatting without changes
uv run ruff format --check .
```

### Building
```bash
# Build package for distribution
uv build

# Build wheel only
uv build --wheel
```

## Architecture

### Core Workflow System (`twpm/core/`)

The workflow system is built on a linked-list architecture where nodes execute sequentially:

1. **Node** (`core/base/node.py`): Abstract base class for all workflow nodes
   - Nodes form a singly-linked list via `next` and `previous` references
   - Each node implements `async execute(data: ListData) -> NodeResult`
   - Node execution is wrapped with `@safe_execute()` decorator to guarantee NodeResult return

2. **Orchestrator** (`core/orchestrator.py`): Main workflow execution engine
   - Manages node execution flow sequentially
   - Maintains shared `ListData` for passing information between nodes
   - Handles node states: `DEFAULT`, `COMPLETE`, `FAILED`, `AWAITING_INPUT`
   - Key methods:
     - `start(start_node)`: Initialize workflow with starting node
     - `process(input=None)`: Execute nodes until completion or input needed
     - `reset()`: Return to beginning of workflow

3. **Node Types** (`core/primitives/`):
   - **TaskNode**: Executes async functions that return bool for success/failure
   - **ConditionalNode**: Branching logic that dynamically inserts next node based on condition
     - Uses `Cursor.insert()` to modify the linked list at runtime
     - Must call `set_condition(condition_func, true_node, false_node)` before execution

4. **Data Flow** (`core/base/models.py`):
   - **ListData**: Dictionary-like container passed between nodes
     - Provides `get()`, `update()`, `has()`, and bracket notation access
   - **NodeResult**: Return value from node execution
     - `success`: bool indicating execution success
     - `data`: dict merged into shared ListData
     - `is_awaiting_input`: pauses workflow for external input
     - `message`: contextual information

5. **Cursor** (`core/cursor.py`): Utility for linked-list manipulation
   - `Cursor.insert(target, new_node)`: Inserts new_node after target
   - Used by ConditionalNode to dynamically modify workflow structure

### Data Structures (`twpm/dsa/`)

Contains learning implementations:
- `linkedlist.py`: Singly-linked list implementation
- `doublelinkedlist.py`: Doubly-linked list implementation

### Testing Pattern

Tests use mock nodes with configurable behavior:
- `MockNode`: Configurable success/failure, data output, awaiting_input state
- `FailingNode`: Raises exceptions to test error handling
- `QuestionNode`: Demonstrates input-awaiting pattern with validation

All tests are async using `@pytest.mark.asyncio`.

## Important Implementation Details

### Safe Execution Decorator
All node `execute()` methods must be decorated with `@safe_execute()`. This decorator:
- Catches exceptions and converts them to failed NodeResult
- Prevents exceptions from propagating to orchestrator
- Logs errors with node identifier

### Workflow Pause/Resume Pattern
Nodes can pause workflow execution by returning `NodeResult(is_awaiting_input=True)`:
1. First `process()` call: node returns `is_awaiting_input=True`, status becomes `AWAITING_INPUT`
2. Orchestrator stops, current node remains set
3. Second `process(input="...")` call: orchestrator provides input via `ListData["_user_input"]`
4. Node processes input and returns regular result to continue workflow

### Dynamic Workflow Modification
ConditionalNode demonstrates runtime workflow structure changes:
- Evaluates condition function
- Uses `Cursor.insert()` to inject appropriate branch into linked list
- Allows for dynamic, data-driven workflow paths

### Node Status Lifecycle
- `DEFAULT`: Ready to execute (reset before each execution)
- `COMPLETE`: Successfully executed
- `FAILED`: Execution failed (stops workflow)
- `AWAITING_INPUT`: Paused waiting for input (workflow can resume)
