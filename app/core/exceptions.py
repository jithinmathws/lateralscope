from __future__ import annotations


class LateralScopeError(Exception):
    """Base exception for all application-specific errors."""


class DomainValidationError(LateralScopeError):
    """Raised when input validation fails at the domain/service layer."""


class ResourceNotFoundError(LateralScopeError):
    """Raised when a required resource or entity cannot be found."""


class GraphError(LateralScopeError):
    """Base exception for graph-related failures."""


class GraphBuildError(GraphError):
    """Raised when the enterprise graph cannot be built safely."""


class NodeNotFoundError(GraphError, ResourceNotFoundError):
    """Raised when a requested node does not exist in the graph."""


class EdgeNotFoundError(GraphError):
    """Raised when an expected edge or edge bundle does not exist."""


class AttackAnalysisError(LateralScopeError):
    """Base exception for attack-path analysis failures."""


class AttackPathNotFoundError(AttackAnalysisError):
    """Raised when no valid attack path exists between source and target."""


class BlastRadiusError(LateralScopeError):
    """Base exception for blast-radius analysis failures."""


class SimulationError(LateralScopeError):
    """Base exception for simulation-related failures."""


class InvalidSimulationRequestError(SimulationError, DomainValidationError):
    """Raised when a simulation request is invalid."""


class ConstraintConflictError(InvalidSimulationRequestError):
    """Raised when mutually exclusive simulation constraints are provided."""