"""A2A Approvals Extension - A Python extension for approving tool calls and actions."""

__version__ = "0.1.0"

from .approvals import (
    ApprovalDecision,
    ApprovalRequest,
    ApprovalResponse,
    ApprovalResult,
    ApprovalsExtension,
    ApprovalStrategy,
    AutoApprovalStrategy,
    InteractiveApprovalStrategy,
    PreApprovedListStrategy,
)

__all__ = [
    "ApprovalDecision",
    "ApprovalRequest",
    "ApprovalResponse",
    "ApprovalResult",
    "ApprovalStrategy",
    "ApprovalsExtension",
    "AutoApprovalStrategy",
    "InteractiveApprovalStrategy",
    "PreApprovedListStrategy",
]
