"""Basic usage example of a2a-approvals extension."""

from a2a_approvals import (
    ApprovalRequest,
    ApprovalsExtension,
    AutoApprovalStrategy,
    PreApprovedListStrategy,
)


def example_auto_approval() -> None:
    """Example using auto-approval strategy."""
    print("=" * 80)
    print("Example 1: Auto-Approval Strategy")
    print("=" * 80)

    # Create extension with auto-approval strategy
    strategy = AutoApprovalStrategy(reason="Development mode - auto-approving all actions")
    extension = ApprovalsExtension(strategy=strategy)

    # Request approval for a file read operation
    request = ApprovalRequest(
        request_id="req-001",
        tool_name="file_reader",
        action="Read configuration file",
        parameters={"file_path": "/etc/config.yml", "mode": "r"},
        risk_level="low",
        justification="Need to load application configuration",
    )

    result = extension.request_approval(request)

    print(f"Request ID: {result.request.request_id}")
    print(f"Tool: {result.request.tool_name}")
    print(f"Action: {result.request.action}")
    print(f"Decision: {result.response.decision}")
    print(f"Approved: {result.approved}")
    print(f"Execution Allowed: {result.execution_allowed}")
    print(f"Reason: {result.response.reason}")
    print()


def example_pre_approved_list() -> None:
    """Example using pre-approved list strategy."""
    print("=" * 80)
    print("Example 2: Pre-Approved List Strategy")
    print("=" * 80)

    # Create extension with pre-approved list
    strategy = PreApprovedListStrategy(
        approved_tools={"file_reader", "calculator", "timer"},
        approved_actions={"Read file", "Calculate sum", "Get current time"},
    )
    extension = ApprovalsExtension(strategy=strategy)

    # Test approved tool
    approved_request = ApprovalRequest(
        request_id="req-002",
        tool_name="calculator",
        action="Calculate sum",
        parameters={"x": 10, "y": 20},
        risk_level="low",
    )

    result1 = extension.request_approval(approved_request)
    print(f"Approved tool - {result1.request.tool_name}:")
    print(f"  Decision: {result1.response.decision}")
    print(f"  Execution Allowed: {result1.execution_allowed}")
    print()

    # Test non-approved tool
    rejected_request = ApprovalRequest(
        request_id="req-003",
        tool_name="database_deleter",
        action="Delete all records",
        parameters={"table": "users"},
        risk_level="critical",
    )

    result2 = extension.request_approval(rejected_request)
    print(f"Non-approved tool - {result2.request.tool_name}:")
    print(f"  Decision: {result2.response.decision}")
    print(f"  Execution Allowed: {result2.execution_allowed}")
    print(f"  Reason: {result2.response.reason}")
    print()

    # Dynamically add a tool to approved list
    print("Adding 'text_processor' to approved list...")
    strategy.add_approved_tool("text_processor")

    new_request = ApprovalRequest(
        request_id="req-004",
        tool_name="text_processor",
        action="Convert to uppercase",
        parameters={"text": "hello world"},
        risk_level="low",
    )

    result3 = extension.request_approval(new_request)
    print(f"Newly approved tool - {result3.request.tool_name}:")
    print(f"  Decision: {result3.response.decision}")
    print(f"  Execution Allowed: {result3.execution_allowed}")
    print()


def example_audit_log() -> None:
    """Example demonstrating audit log functionality."""
    print("=" * 80)
    print("Example 3: Audit Log")
    print("=" * 80)

    strategy = AutoApprovalStrategy()
    extension = ApprovalsExtension(strategy=strategy)

    # Make several approval requests
    tools = ["file_reader", "calculator", "network_client", "database_query"]

    for i, tool in enumerate(tools, 1):
        request = ApprovalRequest(
            request_id=f"req-{i:03d}",
            tool_name=tool,
            action=f"Execute {tool}",
            parameters={"operation": f"operation_{i}"},
        )
        extension.request_approval(request)

    # Review audit log
    print(f"Total approvals in audit log: {len(extension.get_audit_log())}")
    print("\nAudit Log Summary:")
    print("-" * 80)

    for result in extension.get_audit_log():
        print(
            f"  [{result.request.timestamp.strftime('%H:%M:%S')}] "
            f"{result.request.tool_name:20s} - "
            f"{result.response.decision.value:10s} - "
            f"Execution: {'✓' if result.execution_allowed else '✗'}"
        )

    # Export audit log
    exported = extension.export_audit_log()
    print(f"\nExported {len(exported)} audit entries as JSON-compatible dictionaries")
    print()


def example_strict_mode() -> None:
    """Example demonstrating strict mode behavior."""
    print("=" * 80)
    print("Example 4: Strict Mode with Deferred Decisions")
    print("=" * 80)

    # Custom strategy that defers high-risk actions
    def risk_based_callback(request: ApprovalRequest):
        from a2a_approvals import ApprovalDecision, ApprovalResponse

        if request.risk_level in ["critical", "high"]:
            return ApprovalResponse(
                request_id=request.request_id,
                decision=ApprovalDecision.DEFERRED,
                reason=f"High-risk action requires manual review",
            )
        return ApprovalResponse(
            request_id=request.request_id,
            decision=ApprovalDecision.APPROVED,
            reason="Low-risk action auto-approved",
        )

    from a2a_approvals import InteractiveApprovalStrategy

    strategy = InteractiveApprovalStrategy(approval_callback=risk_based_callback)

    # Test with strict mode enabled
    print("Testing with strict_mode=True:")
    strict_extension = ApprovalsExtension(strategy=strategy, strict_mode=True)

    high_risk_request = ApprovalRequest(
        request_id="req-005",
        tool_name="database",
        action="Drop table",
        risk_level="critical",
    )

    result1 = strict_extension.request_approval(high_risk_request)
    print(f"  Decision: {result1.response.decision}")
    print(f"  Execution Allowed: {result1.execution_allowed}")
    print(f"  (Deferred requests are BLOCKED in strict mode)")
    print()

    # Test with strict mode disabled
    print("Testing with strict_mode=False:")
    lenient_extension = ApprovalsExtension(strategy=strategy, strict_mode=False)

    result2 = lenient_extension.request_approval(high_risk_request)
    print(f"  Decision: {result2.response.decision}")
    print(f"  Execution Allowed: {result2.execution_allowed}")
    print(f"  (Deferred requests are ALLOWED in lenient mode)")
    print()


if __name__ == "__main__":
    example_auto_approval()
    example_pre_approved_list()
    example_audit_log()
    example_strict_mode()

    print("=" * 80)
    print("All examples completed!")
    print("=" * 80)
