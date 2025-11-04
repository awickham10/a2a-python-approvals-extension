# A2A Approvals Extension

[![Test](https://github.com/awickham10/a2a-python-approvals-extension/actions/workflows/test.yml/badge.svg)](https://github.com/awickham10/a2a-python-approvals-extension/actions/workflows/test.yml)
[![PyPI version](https://badge.fury.io/py/a2a-approvals.svg)](https://badge.fury.io/py/a2a-approvals)
[![Python Versions](https://img.shields.io/pypi/pyversions/a2a-approvals.svg)](https://pypi.org/project/a2a-approvals/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python extension for the A2A (Agent-to-Agent) protocol that provides approval workflows for tool calls and actions. This extension allows you to implement various approval strategies to control and audit agent behaviors.

## Features

- **Multiple Approval Strategies**: Auto-approval, interactive approval, and pre-approved list strategies
- **Flexible Architecture**: Easy to extend with custom approval strategies
- **Comprehensive Audit Logging**: Track all approval requests and decisions
- **Type-Safe**: Full type hints and mypy-compatible
- **Well-Tested**: Comprehensive test suite with high coverage
- **Production-Ready**: Built with best practices for PyPI distribution

## Installation

Install using pip:

```bash
pip install a2a-approvals
```

Or using uv:

```bash
uv pip install a2a-approvals
```

## Quick Start

```python
from a2a_approvals import (
    ApprovalRequest,
    ApprovalsExtension,
    AutoApprovalStrategy,
)

# Create an approval extension with auto-approval strategy
strategy = AutoApprovalStrategy(reason="Development mode")
extension = ApprovalsExtension(strategy=strategy)

# Request approval for an action
request = ApprovalRequest(
    request_id="req-001",
    tool_name="file_reader",
    action="Read configuration file",
    parameters={"file_path": "/etc/config.yml"},
    risk_level="low",
)

result = extension.request_approval(request)

if result.execution_allowed:
    print(f"Action approved: {result.response.reason}")
else:
    print(f"Action rejected: {result.response.reason}")
```

## Approval Strategies

### Auto-Approval Strategy

Automatically approves all requests (useful for development/testing):

```python
from a2a_approvals import AutoApprovalStrategy, ApprovalsExtension

strategy = AutoApprovalStrategy(reason="Auto-approved in dev mode")
extension = ApprovalsExtension(strategy=strategy)
```

### Pre-Approved List Strategy

Approves based on pre-configured allow lists:

```python
from a2a_approvals import PreApprovedListStrategy, ApprovalsExtension

strategy = PreApprovedListStrategy(
    approved_tools={"calculator", "timer", "file_reader"},
    approved_actions={"Read file", "Calculate sum"},
)
extension = ApprovalsExtension(strategy=strategy)

# Dynamically modify approved lists
strategy.add_approved_tool("text_processor")
strategy.remove_approved_tool("file_reader")
```

### Interactive Approval Strategy

Prompts for manual approval with custom callback:

```python
from a2a_approvals import (
    ApprovalDecision,
    ApprovalRequest,
    ApprovalResponse,
    InteractiveApprovalStrategy,
    ApprovalsExtension,
)

def custom_approval_callback(request: ApprovalRequest) -> ApprovalResponse:
    # Custom approval logic
    if request.risk_level in ["critical", "high"]:
        return ApprovalResponse(
            request_id=request.request_id,
            decision=ApprovalDecision.REJECTED,
            reason="High-risk actions not allowed",
        )
    return ApprovalResponse(
        request_id=request.request_id,
        decision=ApprovalDecision.APPROVED,
        reason="Low-risk action approved",
    )

strategy = InteractiveApprovalStrategy(approval_callback=custom_approval_callback)
extension = ApprovalsExtension(strategy=strategy)
```

### Custom Strategy

Create your own approval strategy:

```python
from a2a_approvals import ApprovalStrategy, ApprovalRequest, ApprovalResponse

class TimeBasedApprovalStrategy(ApprovalStrategy):
    """Approve only during business hours."""

    def evaluate(self, request: ApprovalRequest) -> ApprovalResponse:
        from datetime import datetime

        hour = datetime.now().hour
        if 9 <= hour < 17:  # 9 AM to 5 PM
            return ApprovalResponse(
                request_id=request.request_id,
                decision=ApprovalDecision.APPROVED,
                reason="Within business hours",
            )
        return ApprovalResponse(
            request_id=request.request_id,
            decision=ApprovalDecision.REJECTED,
            reason="Outside business hours",
        )

    def get_strategy_name(self) -> str:
        return "time_based"
```

## Audit Logging

Track all approval decisions:

```python
extension = ApprovalsExtension(strategy=strategy)

# Process multiple requests
for tool in ["file_reader", "database", "network"]:
    request = ApprovalRequest(
        request_id=f"req-{tool}",
        tool_name=tool,
        action=f"Execute {tool}",
    )
    extension.request_approval(request)

# Review audit log
for result in extension.get_audit_log():
    print(f"{result.request.tool_name}: {result.response.decision}")

# Export as JSON
import json
audit_data = extension.export_audit_log()
print(json.dumps(audit_data, indent=2))
```

## Strict Mode

Control behavior for deferred decisions:

```python
# Strict mode (default): deferred requests are blocked
strict_extension = ApprovalsExtension(strategy=strategy, strict_mode=True)

# Lenient mode: deferred requests are allowed to proceed
lenient_extension = ApprovalsExtension(strategy=strategy, strict_mode=False)
```

## Agent Integration Example

```python
from a2a_approvals import ApprovalsExtension, PreApprovedListStrategy

class ApprovalGate:
    def __init__(self, approvals_extension: ApprovalsExtension):
        self.approvals = approvals_extension

    def execute_with_approval(self, tool, action, parameters):
        request = ApprovalRequest(
            request_id=generate_id(),
            tool_name=tool.name,
            action=action,
            parameters=parameters,
            risk_level=tool.risk_level,
        )

        result = self.approvals.request_approval(request)

        if result.execution_allowed:
            return tool.execute(**parameters)
        else:
            raise PermissionError(f"Action not approved: {result.response.reason}")

# Use with agent
strategy = PreApprovedListStrategy(approved_tools={"calculator", "timer"})
extension = ApprovalsExtension(strategy=strategy)
gate = ApprovalGate(extension)
```

## Development

### Setup

1. Clone the repository:
```bash
git clone https://github.com/awickham10/a2a-python-approvals-extension.git
cd a2a-python-approvals-extension
```

2. Install uv if you haven't already:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

3. Install dependencies:
```bash
uv sync --all-extras --dev
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=a2a_approvals --cov-report=html

# Run type checking
uv run mypy src tests

# Run linting
uv run ruff check src tests
uv run ruff format --check src tests
```

### Building

```bash
# Build package
uv build

# Install locally
uv pip install -e .
```

## Examples

See the [examples](./examples) directory for complete working examples:

- [`basic_usage.py`](./examples/basic_usage.py) - Basic usage with different strategies
- [`agent_integration.py`](./examples/agent_integration.py) - Integration with agent systems

Run examples:

```bash
uv run python examples/basic_usage.py
uv run python examples/agent_integration.py
```

## API Reference

### Core Classes

- `ApprovalRequest`: Request for approval of a tool call or action
- `ApprovalResponse`: Response to an approval request
- `ApprovalResult`: Result of processing an approval
- `ApprovalDecision`: Enum of possible decisions (APPROVED, REJECTED, DEFERRED)
- `ApprovalsExtension`: Main extension class for managing approvals
- `ApprovalStrategy`: Abstract base class for approval strategies

### Built-in Strategies

- `AutoApprovalStrategy`: Auto-approves all requests
- `PreApprovedListStrategy`: Approves based on allow lists
- `InteractiveApprovalStrategy`: Uses custom callback for decisions

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and add tests
4. Run tests and linting (`uv run pytest && uv run ruff check`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Related Projects

- [A2A Protocol](https://a2a-protocol.org/) - The Agent-to-Agent protocol specification

## Support

If you encounter any issues or have questions:

- Open an issue on [GitHub](https://github.com/awickham10/a2a-python-approvals-extension/issues)
- Check the [examples](./examples) directory for usage patterns

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes in each release. 
