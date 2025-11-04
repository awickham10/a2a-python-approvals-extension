"""Example of integrating a2a-approvals with an agent system."""

from typing import Any, Callable, Dict

from a2a_approvals import (
    ApprovalRequest,
    ApprovalsExtension,
    PreApprovedListStrategy,
)


class Tool:
    """Simulated tool that requires approval before execution."""

    def __init__(self, name: str, risk_level: str = "medium"):
        """Initialize tool."""
        self.name = name
        self.risk_level = risk_level

    def execute(self, **kwargs: Any) -> str:
        """Execute the tool."""
        return f"Tool '{self.name}' executed with parameters: {kwargs}"


class ApprovalGate:
    """Gate that requires approval before allowing tool execution."""

    def __init__(self, approvals_extension: ApprovalsExtension):
        """Initialize approval gate."""
        self.approvals = approvals_extension
        self._request_counter = 0

    def execute_with_approval(
        self, tool: Tool, action: str, parameters: Dict[str, Any]
    ) -> tuple[bool, str]:
        """
        Execute a tool after getting approval.

        Args:
            tool: The tool to execute
            action: Description of the action
            parameters: Parameters for the tool

        Returns:
            Tuple of (success, result/error message)
        """
        # Generate unique request ID
        self._request_counter += 1
        request_id = f"req-{self._request_counter:05d}"

        # Create approval request
        request = ApprovalRequest(
            request_id=request_id,
            tool_name=tool.name,
            action=action,
            parameters=parameters,
            risk_level=tool.risk_level,
            justification=f"Agent requested to {action}",
        )

        # Request approval
        result = self.approvals.request_approval(request)

        # Check if execution is allowed
        if result.execution_allowed:
            # Use modified parameters if provided, otherwise use originals
            exec_params = result.response.modified_parameters or parameters
            output = tool.execute(**exec_params)
            return True, output
        else:
            return False, f"Action rejected: {result.response.reason}"


class SimpleAgent:
    """Simulated agent that uses tools with approval requirements."""

    def __init__(self, approval_gate: ApprovalGate):
        """Initialize agent."""
        self.approval_gate = approval_gate
        self.tools: Dict[str, Tool] = {}

    def register_tool(self, tool: Tool) -> None:
        """Register a tool with the agent."""
        self.tools[tool.name] = tool

    def use_tool(self, tool_name: str, action: str, **parameters: Any) -> str:
        """
        Use a tool to perform an action.

        Args:
            tool_name: Name of the tool to use
            action: Description of the action
            **parameters: Tool parameters

        Returns:
            Result message
        """
        if tool_name not in self.tools:
            return f"Error: Tool '{tool_name}' not found"

        tool = self.tools[tool_name]
        success, result = self.approval_gate.execute_with_approval(tool, action, parameters)

        if success:
            return f"✓ Success: {result}"
        else:
            return f"✗ Failed: {result}"


def main() -> None:
    """Demonstrate agent integration with approval system."""
    print("=" * 80)
    print("Agent Integration Example")
    print("=" * 80)
    print()

    # Set up approval system with pre-approved safe tools
    strategy = PreApprovedListStrategy(
        approved_tools={"calculator", "timer", "text_formatter"},
        approved_actions={
            "Calculate sum",
            "Get current time",
            "Format text",
            "Read file",  # Specific read action is approved
        },
    )
    approvals_extension = ApprovalsExtension(strategy=strategy, strict_mode=True)

    # Create approval gate
    approval_gate = ApprovalGate(approvals_extension)

    # Create agent
    agent = SimpleAgent(approval_gate)

    # Register tools with different risk levels
    agent.register_tool(Tool("calculator", risk_level="low"))
    agent.register_tool(Tool("timer", risk_level="low"))
    agent.register_tool(Tool("file_system", risk_level="medium"))
    agent.register_tool(Tool("database", risk_level="high"))
    agent.register_tool(Tool("network", risk_level="medium"))

    # Simulate agent performing various actions
    print("Agent performing actions:")
    print("-" * 80)

    # Safe, approved action
    print("\n1. Using pre-approved calculator:")
    result = agent.use_tool("calculator", "Calculate sum", x=10, y=20)
    print(f"   {result}")

    # Safe, approved action
    print("\n2. Using pre-approved timer:")
    result = agent.use_tool("timer", "Get current time", format="ISO")
    print(f"   {result}")

    # Medium risk, specific action approved
    print("\n3. File read (approved action):")
    result = agent.use_tool("file_system", "Read file", path="/etc/config.yml")
    print(f"   {result}")

    # Medium risk, action not approved
    print("\n4. File write (not approved):")
    result = agent.use_tool("file_system", "Write file", path="/etc/config.yml", data="...")
    print(f"   {result}")

    # High risk, not approved
    print("\n5. Database operation (not approved):")
    result = agent.use_tool("database", "Delete records", table="users", where="age > 30")
    print(f"   {result}")

    # Review audit log
    print("\n" + "=" * 80)
    print("Approval Audit Log:")
    print("=" * 80)

    audit_log = approvals_extension.get_audit_log()
    print(f"Total requests: {len(audit_log)}")
    print(f"Approved: {sum(1 for r in audit_log if r.approved)}")
    print(f"Rejected: {sum(1 for r in audit_log if not r.approved)}")
    print()

    print("Detailed log:")
    print("-" * 80)
    for entry in audit_log:
        status = "✓ APPROVED" if entry.approved else "✗ REJECTED"
        print(f"{status:12s} | {entry.request.tool_name:15s} | {entry.request.action}")

    print()


if __name__ == "__main__":
    main()
