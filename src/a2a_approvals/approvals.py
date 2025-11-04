"""Core approval extension functionality for A2A protocol."""

from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional

from pydantic import BaseModel, ConfigDict, Field


class ApprovalDecision(str, Enum):
    """Possible approval decisions."""

    APPROVED = "approved"
    REJECTED = "rejected"
    DEFERRED = "deferred"  # Request more information before deciding


class ApprovalRequest(BaseModel):
    """Request for approval of a tool call or action."""

    request_id: str = Field(..., description="Unique identifier for this approval request")
    tool_name: str = Field(..., description="Name of the tool being called")
    action: str = Field(..., description="Description of the action to be performed")
    parameters: dict[str, Any] = Field(
        default_factory=dict, description="Parameters for the tool call"
    )
    context: dict[str, Any] = Field(
        default_factory=dict, description="Additional context for the approval decision"
    )
    timestamp: datetime = Field(default_factory=datetime.now, description="Request timestamp")
    risk_level: str = Field(
        default="medium", description="Risk level: low, medium, high, critical"
    )
    justification: Optional[str] = Field(
        None, description="Justification for why this action is needed"
    )

    model_config = ConfigDict(
        json_encoders={datetime: lambda v: v.isoformat()},
    )


class ApprovalResponse(BaseModel):
    """Response to an approval request."""

    request_id: str = Field(..., description="ID of the approval request")
    decision: ApprovalDecision = Field(..., description="The approval decision")
    reason: Optional[str] = Field(None, description="Reason for the decision")
    modified_parameters: Optional[dict[str, Any]] = Field(
        None, description="Modified parameters if approved with changes"
    )
    expires_at: Optional[datetime] = Field(
        None, description="Expiration time for this approval"
    )
    approver: Optional[str] = Field(None, description="Identifier of who/what approved")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")

    model_config = ConfigDict(
        json_encoders={datetime: lambda v: v.isoformat()},
    )


class ApprovalResult(BaseModel):
    """Result of processing an approval."""

    approved: bool = Field(..., description="Whether the action was approved")
    request: ApprovalRequest = Field(..., description="Original approval request")
    response: ApprovalResponse = Field(..., description="Approval response")
    execution_allowed: bool = Field(
        ..., description="Whether execution should proceed based on approval"
    )


class ApprovalStrategy(ABC):
    """Abstract base class for approval strategies."""

    @abstractmethod
    def evaluate(self, request: ApprovalRequest) -> ApprovalResponse:
        """
        Evaluate an approval request and return a decision.

        Args:
            request: The approval request to evaluate

        Returns:
            ApprovalResponse with the decision
        """
        pass

    @abstractmethod
    def get_strategy_name(self) -> str:
        """Return the name of this strategy."""
        pass


class AutoApprovalStrategy(ApprovalStrategy):
    """Strategy that automatically approves all requests (use with caution)."""

    def __init__(self, reason: str = "Auto-approved"):
        """
        Initialize auto-approval strategy.

        Args:
            reason: Reason to include in approval responses
        """
        self.reason = reason

    def evaluate(self, request: ApprovalRequest) -> ApprovalResponse:
        """Auto-approve all requests."""
        return ApprovalResponse(
            request_id=request.request_id,
            decision=ApprovalDecision.APPROVED,
            reason=self.reason,
            approver="AutoApprovalStrategy",
        )

    def get_strategy_name(self) -> str:
        """Return strategy name."""
        return "auto_approve"


class InteractiveApprovalStrategy(ApprovalStrategy):
    """Strategy that prompts for interactive approval."""

    def __init__(
        self,
        approval_callback: Optional[Callable[[ApprovalRequest], ApprovalResponse]] = None,
    ):
        """
        Initialize interactive approval strategy.

        Args:
            approval_callback: Optional callback function for custom approval logic.
                             If None, uses default console-based approval.
        """
        self.approval_callback = approval_callback or self._default_console_approval

    def _default_console_approval(self, request: ApprovalRequest) -> ApprovalResponse:
        """Default console-based approval prompt."""
        print("\n" + "=" * 80)
        print("APPROVAL REQUEST")
        print("=" * 80)
        print(f"Request ID: {request.request_id}")
        print(f"Tool: {request.tool_name}")
        print(f"Action: {request.action}")
        print(f"Risk Level: {request.risk_level}")
        if request.justification:
            print(f"Justification: {request.justification}")
        print("\nParameters:")
        for key, value in request.parameters.items():
            print(f"  {key}: {value}")
        print("=" * 80)

        while True:
            choice = input("\nApprove this action? [y/n/d(defer)]: ").strip().lower()
            if choice in ["y", "yes"]:
                return ApprovalResponse(
                    request_id=request.request_id,
                    decision=ApprovalDecision.APPROVED,
                    reason="Approved by user",
                    approver="InteractiveApprovalStrategy",
                )
            elif choice in ["n", "no"]:
                reason = input("Reason for rejection (optional): ").strip()
                return ApprovalResponse(
                    request_id=request.request_id,
                    decision=ApprovalDecision.REJECTED,
                    reason=reason or "Rejected by user",
                    approver="InteractiveApprovalStrategy",
                )
            elif choice in ["d", "defer"]:
                reason = input("Reason for deferral (optional): ").strip()
                return ApprovalResponse(
                    request_id=request.request_id,
                    decision=ApprovalDecision.DEFERRED,
                    reason=reason or "Deferred by user",
                    approver="InteractiveApprovalStrategy",
                )
            else:
                print("Invalid choice. Please enter 'y', 'n', or 'd'.")

    def evaluate(self, request: ApprovalRequest) -> ApprovalResponse:
        """Prompt for interactive approval."""
        return self.approval_callback(request)

    def get_strategy_name(self) -> str:
        """Return strategy name."""
        return "interactive"


class PreApprovedListStrategy(ApprovalStrategy):
    """Strategy that approves based on a pre-approved list of tools/actions."""

    def __init__(
        self,
        approved_tools: Optional[set[str]] = None,
        approved_actions: Optional[set[str]] = None,
        default_decision: ApprovalDecision = ApprovalDecision.REJECTED,
    ):
        """
        Initialize pre-approved list strategy.

        Args:
            approved_tools: Set of pre-approved tool names
            approved_actions: Set of pre-approved action descriptions
            default_decision: Decision to use if not in approved list
        """
        self.approved_tools = approved_tools or set()
        self.approved_actions = approved_actions or set()
        self.default_decision = default_decision

    def evaluate(self, request: ApprovalRequest) -> ApprovalResponse:
        """Evaluate based on pre-approved lists."""
        is_approved = (
            request.tool_name in self.approved_tools or request.action in self.approved_actions
        )

        if is_approved:
            return ApprovalResponse(
                request_id=request.request_id,
                decision=ApprovalDecision.APPROVED,
                reason=f"Tool '{request.tool_name}' or action '{request.action}' is pre-approved",
                approver="PreApprovedListStrategy",
            )
        else:
            return ApprovalResponse(
                request_id=request.request_id,
                decision=self.default_decision,
                reason=f"Tool '{request.tool_name}' not in pre-approved list",
                approver="PreApprovedListStrategy",
            )

    def add_approved_tool(self, tool_name: str) -> None:
        """Add a tool to the approved list."""
        self.approved_tools.add(tool_name)

    def add_approved_action(self, action: str) -> None:
        """Add an action to the approved list."""
        self.approved_actions.add(action)

    def remove_approved_tool(self, tool_name: str) -> None:
        """Remove a tool from the approved list."""
        self.approved_tools.discard(tool_name)

    def remove_approved_action(self, action: str) -> None:
        """Remove an action from the approved list."""
        self.approved_actions.discard(action)

    def get_strategy_name(self) -> str:
        """Return strategy name."""
        return "pre_approved_list"


class ApprovalsExtension:
    """Main A2A approvals extension class."""

    def __init__(
        self,
        strategy: ApprovalStrategy,
        strict_mode: bool = True,
        audit_log: Optional[list[ApprovalResult]] = None,
    ):
        """
        Initialize the approvals extension.

        Args:
            strategy: The approval strategy to use
            strict_mode: If True, reject deferred requests; if False, treat as approved
            audit_log: Optional list to store approval results for auditing
        """
        self.strategy = strategy
        self.strict_mode = strict_mode
        self.audit_log = audit_log if audit_log is not None else []
        self._pending_requests: dict[str, ApprovalRequest] = {}

    def request_approval(self, request: ApprovalRequest) -> ApprovalResult:
        """
        Request approval for a tool call or action.

        Args:
            request: The approval request

        Returns:
            ApprovalResult containing the decision and execution permission
        """
        # Store pending request
        self._pending_requests[request.request_id] = request

        # Evaluate using strategy
        response = self.strategy.evaluate(request)

        # Determine execution permission
        if response.decision == ApprovalDecision.APPROVED:
            execution_allowed = True
            approved = True
        elif response.decision == ApprovalDecision.REJECTED:
            execution_allowed = False
            approved = False
        else:  # DEFERRED
            execution_allowed = not self.strict_mode
            approved = False

        # Create result
        result = ApprovalResult(
            approved=approved,
            request=request,
            response=response,
            execution_allowed=execution_allowed,
        )

        # Add to audit log
        self.audit_log.append(result)

        # Remove from pending
        self._pending_requests.pop(request.request_id, None)

        return result

    def get_pending_requests(self) -> list[ApprovalRequest]:
        """Get list of pending approval requests."""
        return list(self._pending_requests.values())

    def get_audit_log(self) -> list[ApprovalResult]:
        """Get the full audit log of approval results."""
        return self.audit_log.copy()

    def clear_audit_log(self) -> None:
        """Clear the audit log."""
        self.audit_log.clear()

    def set_strategy(self, strategy: ApprovalStrategy) -> None:
        """Change the approval strategy."""
        self.strategy = strategy

    def export_audit_log(self) -> list[dict[str, Any]]:
        """
        Export audit log as JSON-serializable dictionaries.

        Returns:
            List of approval results as dictionaries
        """
        return [
            {
                "approved": result.approved,
                "execution_allowed": result.execution_allowed,
                "request": result.request.model_dump(),
                "response": result.response.model_dump(),
            }
            for result in self.audit_log
        ]
