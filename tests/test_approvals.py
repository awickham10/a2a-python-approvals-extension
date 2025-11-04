"""Tests for approval extension functionality."""

from datetime import datetime

from a2a_approvals import (
    ApprovalDecision,
    ApprovalRequest,
    ApprovalResponse,
    ApprovalResult,
    ApprovalsExtension,
    AutoApprovalStrategy,
    InteractiveApprovalStrategy,
    PreApprovedListStrategy,
)


class TestApprovalRequest:
    """Tests for ApprovalRequest model."""

    def test_create_minimal_request(self) -> None:
        """Test creating a minimal approval request."""
        request = ApprovalRequest(
            request_id="test-001",
            tool_name="file_reader",
            action="Read configuration file",
        )
        assert request.request_id == "test-001"
        assert request.tool_name == "file_reader"
        assert request.action == "Read configuration file"
        assert request.parameters == {}
        assert request.risk_level == "medium"
        assert isinstance(request.timestamp, datetime)

    def test_create_full_request(self) -> None:
        """Test creating a full approval request with all fields."""
        params = {"file_path": "/etc/config.yml", "mode": "read"}
        context = {"user": "admin", "session_id": "abc123"}

        request = ApprovalRequest(
            request_id="test-002",
            tool_name="file_reader",
            action="Read configuration file",
            parameters=params,
            context=context,
            risk_level="low",
            justification="Required for initialization",
        )

        assert request.parameters == params
        assert request.context == context
        assert request.risk_level == "low"
        assert request.justification == "Required for initialization"

    def test_request_serialization(self) -> None:
        """Test that request can be serialized to dict."""
        request = ApprovalRequest(
            request_id="test-003",
            tool_name="database",
            action="Query users table",
        )
        data = request.model_dump()
        assert isinstance(data, dict)
        assert data["request_id"] == "test-003"
        assert data["tool_name"] == "database"


class TestApprovalResponse:
    """Tests for ApprovalResponse model."""

    def test_create_approved_response(self) -> None:
        """Test creating an approved response."""
        response = ApprovalResponse(
            request_id="test-001",
            decision=ApprovalDecision.APPROVED,
            reason="Safe operation",
            approver="admin",
        )
        assert response.request_id == "test-001"
        assert response.decision == ApprovalDecision.APPROVED
        assert response.reason == "Safe operation"
        assert response.approver == "admin"

    def test_create_rejected_response(self) -> None:
        """Test creating a rejected response."""
        response = ApprovalResponse(
            request_id="test-002",
            decision=ApprovalDecision.REJECTED,
            reason="Insufficient permissions",
        )
        assert response.decision == ApprovalDecision.REJECTED
        assert response.reason == "Insufficient permissions"

    def test_response_with_modified_parameters(self) -> None:
        """Test response with modified parameters."""
        modified = {"timeout": 30, "retries": 3}
        response = ApprovalResponse(
            request_id="test-003",
            decision=ApprovalDecision.APPROVED,
            modified_parameters=modified,
        )
        assert response.modified_parameters == modified


class TestAutoApprovalStrategy:
    """Tests for AutoApprovalStrategy."""

    def test_auto_approve(self) -> None:
        """Test that auto approval strategy approves all requests."""
        strategy = AutoApprovalStrategy(reason="Testing auto-approval")
        request = ApprovalRequest(
            request_id="test-001",
            tool_name="any_tool",
            action="Any action",
        )

        response = strategy.evaluate(request)

        assert response.decision == ApprovalDecision.APPROVED
        assert response.reason == "Testing auto-approval"
        assert response.approver == "AutoApprovalStrategy"
        assert response.request_id == "test-001"

    def test_strategy_name(self) -> None:
        """Test strategy name."""
        strategy = AutoApprovalStrategy()
        assert strategy.get_strategy_name() == "auto_approve"


class TestPreApprovedListStrategy:
    """Tests for PreApprovedListStrategy."""

    def test_approve_tool_in_list(self) -> None:
        """Test approving a tool in the pre-approved list."""
        strategy = PreApprovedListStrategy(
            approved_tools={"file_reader", "calculator"}
        )
        request = ApprovalRequest(
            request_id="test-001",
            tool_name="file_reader",
            action="Read file",
        )

        response = strategy.evaluate(request)

        assert response.decision == ApprovalDecision.APPROVED
        assert response.reason is not None and "pre-approved" in response.reason.lower()

    def test_reject_tool_not_in_list(self) -> None:
        """Test rejecting a tool not in the pre-approved list."""
        strategy = PreApprovedListStrategy(
            approved_tools={"file_reader"}
        )
        request = ApprovalRequest(
            request_id="test-001",
            tool_name="database_writer",
            action="Delete records",
        )

        response = strategy.evaluate(request)

        assert response.decision == ApprovalDecision.REJECTED
        assert response.reason is not None and "not in pre-approved list" in response.reason

    def test_approve_action_in_list(self) -> None:
        """Test approving an action in the pre-approved list."""
        strategy = PreApprovedListStrategy(
            approved_actions={"Read file", "List directory"}
        )
        request = ApprovalRequest(
            request_id="test-001",
            tool_name="file_system",
            action="Read file",
        )

        response = strategy.evaluate(request)

        assert response.decision == ApprovalDecision.APPROVED

    def test_add_approved_tool(self) -> None:
        """Test adding a tool to the approved list."""
        strategy = PreApprovedListStrategy()
        assert "new_tool" not in strategy.approved_tools

        strategy.add_approved_tool("new_tool")

        assert "new_tool" in strategy.approved_tools

    def test_remove_approved_tool(self) -> None:
        """Test removing a tool from the approved list."""
        strategy = PreApprovedListStrategy(
            approved_tools={"tool1", "tool2"}
        )

        strategy.remove_approved_tool("tool1")

        assert "tool1" not in strategy.approved_tools
        assert "tool2" in strategy.approved_tools

    def test_strategy_name(self) -> None:
        """Test strategy name."""
        strategy = PreApprovedListStrategy()
        assert strategy.get_strategy_name() == "pre_approved_list"


class TestInteractiveApprovalStrategy:
    """Tests for InteractiveApprovalStrategy."""

    def test_custom_callback(self) -> None:
        """Test interactive strategy with custom callback."""

        def custom_approver(request: ApprovalRequest) -> ApprovalResponse:
            # Auto-approve if risk is low
            if request.risk_level == "low":
                return ApprovalResponse(
                    request_id=request.request_id,
                    decision=ApprovalDecision.APPROVED,
                    reason="Low risk auto-approved",
                )
            return ApprovalResponse(
                request_id=request.request_id,
                decision=ApprovalDecision.REJECTED,
                reason="High risk rejected",
            )

        strategy = InteractiveApprovalStrategy(approval_callback=custom_approver)

        # Test low risk
        low_risk_request = ApprovalRequest(
            request_id="test-001",
            tool_name="calculator",
            action="Add numbers",
            risk_level="low",
        )
        response = strategy.evaluate(low_risk_request)
        assert response.decision == ApprovalDecision.APPROVED

        # Test high risk
        high_risk_request = ApprovalRequest(
            request_id="test-002",
            tool_name="database",
            action="Drop table",
            risk_level="high",
        )
        response = strategy.evaluate(high_risk_request)
        assert response.decision == ApprovalDecision.REJECTED

    def test_strategy_name(self) -> None:
        """Test strategy name."""
        strategy = InteractiveApprovalStrategy(
            approval_callback=lambda r: ApprovalResponse(
                request_id=r.request_id, decision=ApprovalDecision.APPROVED
            )
        )
        assert strategy.get_strategy_name() == "interactive"


class TestApprovalsExtension:
    """Tests for ApprovalsExtension."""

    def test_request_approval_approved(self) -> None:
        """Test requesting approval that gets approved."""
        strategy = AutoApprovalStrategy()
        extension = ApprovalsExtension(strategy=strategy)

        request = ApprovalRequest(
            request_id="test-001",
            tool_name="calculator",
            action="Calculate sum",
        )

        result = extension.request_approval(request)

        assert isinstance(result, ApprovalResult)
        assert result.approved is True
        assert result.execution_allowed is True
        assert result.request == request

    def test_request_approval_rejected(self) -> None:
        """Test requesting approval that gets rejected."""
        strategy = PreApprovedListStrategy(approved_tools=set())
        extension = ApprovalsExtension(strategy=strategy)

        request = ApprovalRequest(
            request_id="test-001",
            tool_name="dangerous_tool",
            action="Dangerous action",
        )

        result = extension.request_approval(request)

        assert result.approved is False
        assert result.execution_allowed is False

    def test_audit_log(self) -> None:
        """Test that approvals are logged in audit log."""
        strategy = AutoApprovalStrategy()
        extension = ApprovalsExtension(strategy=strategy)

        assert len(extension.get_audit_log()) == 0

        request1 = ApprovalRequest(
            request_id="test-001", tool_name="tool1", action="Action 1"
        )
        request2 = ApprovalRequest(
            request_id="test-002", tool_name="tool2", action="Action 2"
        )

        extension.request_approval(request1)
        extension.request_approval(request2)

        audit_log = extension.get_audit_log()
        assert len(audit_log) == 2
        assert audit_log[0].request.request_id == "test-001"
        assert audit_log[1].request.request_id == "test-002"

    def test_clear_audit_log(self) -> None:
        """Test clearing the audit log."""
        strategy = AutoApprovalStrategy()
        extension = ApprovalsExtension(strategy=strategy)

        request = ApprovalRequest(
            request_id="test-001", tool_name="tool", action="Action"
        )
        extension.request_approval(request)

        assert len(extension.get_audit_log()) == 1

        extension.clear_audit_log()

        assert len(extension.get_audit_log()) == 0

    def test_export_audit_log(self) -> None:
        """Test exporting audit log as JSON."""
        strategy = AutoApprovalStrategy()
        extension = ApprovalsExtension(strategy=strategy)

        request = ApprovalRequest(
            request_id="test-001",
            tool_name="calculator",
            action="Calculate",
            parameters={"x": 1, "y": 2},
        )
        extension.request_approval(request)

        exported = extension.export_audit_log()

        assert len(exported) == 1
        assert isinstance(exported[0], dict)
        assert exported[0]["approved"] is True
        assert exported[0]["request"]["tool_name"] == "calculator"

    def test_strict_mode_deferred(self) -> None:
        """Test strict mode with deferred decisions."""

        def defer_callback(request: ApprovalRequest) -> ApprovalResponse:
            return ApprovalResponse(
                request_id=request.request_id,
                decision=ApprovalDecision.DEFERRED,
                reason="Needs review",
            )

        strategy = InteractiveApprovalStrategy(approval_callback=defer_callback)

        # Test strict mode (default)
        strict_extension = ApprovalsExtension(strategy=strategy, strict_mode=True)
        request = ApprovalRequest(
            request_id="test-001", tool_name="tool", action="Action"
        )
        result = strict_extension.request_approval(request)

        assert result.approved is False
        assert result.execution_allowed is False

        # Test non-strict mode
        lenient_extension = ApprovalsExtension(strategy=strategy, strict_mode=False)
        request2 = ApprovalRequest(
            request_id="test-002", tool_name="tool", action="Action"
        )
        result2 = lenient_extension.request_approval(request2)

        assert result2.approved is False
        assert result2.execution_allowed is True

    def test_change_strategy(self) -> None:
        """Test changing approval strategy."""
        auto_strategy = AutoApprovalStrategy()
        extension = ApprovalsExtension(strategy=auto_strategy)

        request = ApprovalRequest(
            request_id="test-001", tool_name="tool", action="Action"
        )
        result1 = extension.request_approval(request)
        assert result1.approved is True

        # Change to restrictive strategy
        restrictive_strategy = PreApprovedListStrategy(approved_tools=set())
        extension.set_strategy(restrictive_strategy)

        request2 = ApprovalRequest(
            request_id="test-002", tool_name="tool", action="Action"
        )
        result2 = extension.request_approval(request2)
        assert result2.approved is False

    def test_pending_requests_cleared(self) -> None:
        """Test that pending requests are cleared after processing."""
        strategy = AutoApprovalStrategy()
        extension = ApprovalsExtension(strategy=strategy)

        request = ApprovalRequest(
            request_id="test-001", tool_name="tool", action="Action"
        )

        # Before approval
        extension._pending_requests[request.request_id] = request
        assert len(extension.get_pending_requests()) == 1

        # After approval
        extension.request_approval(request)
        assert len(extension.get_pending_requests()) == 0
