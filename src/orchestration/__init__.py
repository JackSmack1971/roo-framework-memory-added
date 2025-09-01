"""
Quality Threshold Orchestration Module

This module provides centralized management of dynamic quality thresholds
for the autonomous AI development framework.
"""

from .main import (
    QualityThresholdOrchestrator,
    OrchestratorUpdateError,
    ThresholdConfig,
    trigger_threshold_recalculation,
    get_orchestrator
)

__all__ = [
    'QualityThresholdOrchestrator',
    'OrchestratorUpdateError',
    'ThresholdConfig',
    'trigger_threshold_recalculation',
    'get_orchestrator'
]

__version__ = "1.0.0"