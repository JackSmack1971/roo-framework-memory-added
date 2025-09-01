"""
Quality Threshold Orchestrator

Manages dynamic quality thresholds based on project phase transitions and learning feedback.
Provides centralized threshold management for the autonomous development framework.
"""

import asyncio
import json
import os
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime, timedelta
import aiofiles

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OrchestratorUpdateError(Exception):
    """Custom exception for orchestrator update failures"""

    def __init__(self, message: str, cause: Optional[Exception] = None):
        super().__init__(message)
        self.cause = cause


@dataclass
class ThresholdConfig:
    """Configuration for quality thresholds"""
    project_phase: str
    gate_thresholds: Dict[str, float]
    learning_adjustments: Dict[str, float]
    updated_at: str


class QualityThresholdOrchestrator:
    """
    Orchestrates dynamic quality threshold management for autonomous development.

    Handles phase transitions, learning feedback integration, and threshold recalculation
    with robust error handling and retry mechanisms.
    """

    def __init__(self, dashboard_path: Optional[str] = None, timeout_ms: int = 5000):
        temp_path = dashboard_path or os.getenv('QUALITY_DASHBOARD_PATH')
        if not temp_path:
            raise ValueError("QUALITY_DASHBOARD_PATH environment variable must be set")
        # Type assertion after validation
        self.dashboard_path: str = temp_path

        self.timeout_ms = timeout_ms
        self._lock = asyncio.Lock()
        self._last_config: Optional[ThresholdConfig] = None

        # Phase transition multipliers
        self.phase_multipliers = {
            'init': {
                'security': 0.7, 'performance': 0.6, 'code': 0.8, 'architecture': 0.5, 'general': 0.7,
                'api_documentation': 0.6, 'code_documentation': 0.7, 'architecture_documentation': 0.4, 'usage_documentation': 0.8
            },
            'dev': {
                'security': 0.8, 'performance': 0.7, 'code': 0.9, 'architecture': 0.7, 'general': 0.8,
                'api_documentation': 0.7, 'code_documentation': 0.8, 'architecture_documentation': 0.6, 'usage_documentation': 0.9
            },
            'stabilization': {
                'security': 1.0, 'performance': 0.9, 'code': 1.0, 'architecture': 0.9, 'general': 0.9,
                'api_documentation': 0.9, 'code_documentation': 1.0, 'architecture_documentation': 0.8, 'usage_documentation': 1.0
            },
            'release': {
                'security': 1.1, 'performance': 1.0, 'code': 1.0, 'architecture': 1.0, 'general': 1.0,
                'api_documentation': 1.0, 'code_documentation': 1.0, 'architecture_documentation': 1.0, 'usage_documentation': 1.0
            }
        }

        logger.info(f"Initialized QualityThresholdOrchestrator with dashboard: {self.dashboard_path}")

    async def read_current_config(self, retries: int = 3) -> ThresholdConfig:
        """
        Read current threshold configuration from dashboard with retry logic.

        Args:
            retries: Number of retry attempts

        Returns:
            Current threshold configuration

        Raises:
            OrchestratorUpdateError: If configuration cannot be read
        """
        for attempt in range(retries):
            try:
                async with aiofiles.open(self.dashboard_path, 'r') as f:
                    content = await asyncio.wait_for(f.read(), timeout=self.timeout_ms / 1000)
                    config_data = json.loads(content)

                    # Validate required fields
                    if 'project_phase' not in config_data:
                        raise ValueError("Missing project_phase in dashboard configuration")
                    if 'gate_thresholds' not in config_data:
                        raise ValueError("Missing gate_thresholds in dashboard configuration")
                    if 'learning_adjustments' not in config_data:
                        raise ValueError("Missing learning_adjustments in dashboard configuration")

                    config = ThresholdConfig(
                        project_phase=config_data['project_phase'],
                        gate_thresholds=config_data['gate_thresholds'],
                        learning_adjustments=config_data['learning_adjustments'],
                        updated_at=config_data.get('updated_at', datetime.now().isoformat())
                    )

                    self._last_config = config
                    return config

            except (FileNotFoundError, json.JSONDecodeError, asyncio.TimeoutError) as e:
                if attempt == retries - 1:
                    raise OrchestratorUpdateError(f"Failed to read dashboard config after {retries} attempts", e)

                # Exponential backoff
                await asyncio.sleep(0.1 * (2 ** attempt))

        raise OrchestratorUpdateError("Unexpected error in read_current_config")

    async def write_config(self, config: ThresholdConfig, retries: int = 3) -> None:
        """
        Write threshold configuration to dashboard with retry logic.

        Args:
            config: Configuration to write
            retries: Number of retry attempts

        Raises:
            OrchestratorUpdateError: If configuration cannot be written
        """
        async with self._lock:
            for attempt in range(retries):
                try:
                    # Read current dashboard content to preserve other fields
                    async with aiofiles.open(self.dashboard_path, 'r') as f:
                        current_content = await asyncio.wait_for(f.read(), timeout=self.timeout_ms / 1000)
                        dashboard_data = json.loads(current_content)

                    # Update threshold-related fields
                    dashboard_data['project_phase'] = config.project_phase
                    dashboard_data['gate_thresholds'] = config.gate_thresholds
                    dashboard_data['learning_adjustments'] = config.learning_adjustments
                    dashboard_data['updated_at'] = datetime.now().isoformat()

                    # Write updated configuration
                    async with aiofiles.open(self.dashboard_path, 'w') as f:
                        await asyncio.wait_for(
                            f.write(json.dumps(dashboard_data, indent=2)),
                            timeout=self.timeout_ms / 1000
                        )

                    logger.info(f"Successfully updated quality thresholds for phase: {config.project_phase}")
                    return

                except (FileNotFoundError, json.JSONDecodeError, asyncio.TimeoutError) as e:
                    if attempt == retries - 1:
                        raise OrchestratorUpdateError(f"Failed to write dashboard config after {retries} attempts", e)

                    # Exponential backoff
                    await asyncio.sleep(0.1 * (2 ** attempt))

    async def handle_phase_transition(self, new_phase: str, feedback_data: Optional[Dict[str, Any]] = None) -> ThresholdConfig:
        """
        Handle project phase transition and recalculate thresholds.

        Args:
            new_phase: New project phase (init, dev, stabilization, release)
            feedback_data: Optional learning feedback data

        Returns:
            Updated threshold configuration

        Raises:
            OrchestratorUpdateError: If transition fails
        """
        if new_phase not in self.phase_multipliers:
            raise OrchestratorUpdateError(f"Invalid project phase: {new_phase}")

        try:
            current_config = await self.read_current_config()

            # Calculate new thresholds based on phase
            new_thresholds = self._calculate_phase_thresholds(new_phase, current_config.gate_thresholds)

            # Apply learning adjustments if feedback provided
            new_adjustments = current_config.learning_adjustments.copy()
            if feedback_data:
                new_adjustments = self._apply_learning_feedback(new_adjustments, feedback_data)

            # Create updated configuration
            updated_config = ThresholdConfig(
                project_phase=new_phase,
                gate_thresholds=new_thresholds,
                learning_adjustments=new_adjustments,
                updated_at=datetime.now().isoformat()
            )

            # Write updated configuration
            await self.write_config(updated_config)

            logger.info(f"Phase transition completed: {current_config.project_phase} -> {new_phase}")
            return updated_config

        except Exception as e:
            raise OrchestratorUpdateError(f"Phase transition failed: {str(e)}", e)

    async def update_learning_adjustments(self, feedback_data: Dict[str, Any]) -> ThresholdConfig:
        """
        Update learning adjustments based on feedback data.

        Args:
            feedback_data: Learning feedback containing gate performance metrics

        Returns:
            Updated threshold configuration

        Raises:
            OrchestratorUpdateError: If update fails
        """
        try:
            current_config = await self.read_current_config()

            # Apply learning feedback to adjustments
            new_adjustments = self._apply_learning_feedback(current_config.learning_adjustments, feedback_data)

            # Create updated configuration
            updated_config = ThresholdConfig(
                project_phase=current_config.project_phase,
                gate_thresholds=current_config.gate_thresholds,
                learning_adjustments=new_adjustments,
                updated_at=datetime.now().isoformat()
            )

            # Write updated configuration
            await self.write_config(updated_config)

            logger.info("Learning adjustments updated based on feedback data")
            return updated_config

        except Exception as e:
            raise OrchestratorUpdateError(f"Learning adjustment update failed: {str(e)}", e)

    def _calculate_phase_thresholds(self, phase: str, base_thresholds: Dict[str, float]) -> Dict[str, float]:
        """Calculate phase-specific thresholds based on base values and phase multipliers."""
        multipliers = self.phase_multipliers[phase]
        new_thresholds = {}

        for gate_type, base_threshold in base_thresholds.items():
            multiplier = multipliers.get(gate_type, multipliers.get('general', 1.0))
            # Ensure thresholds stay within valid range [0, 1]
            new_thresholds[gate_type] = max(0.0, min(1.0, base_threshold * multiplier))

        return new_thresholds

    def _apply_learning_feedback(self, current_adjustments: Dict[str, float], feedback_data: Dict[str, Any]) -> Dict[str, float]:
        """Apply learning feedback to threshold adjustments."""
        new_adjustments = current_adjustments.copy()
        learning_rate = 0.1  # Conservative learning rate

        # Process gate-specific feedback
        for gate_type, metrics in feedback_data.items():
            if gate_type not in new_adjustments:
                new_adjustments[gate_type] = 0.0

            if isinstance(metrics, dict) and 'success_rate' in metrics:
                success_rate = metrics['success_rate']

                # Adjust based on success rate
                if success_rate > 0.9:  # Too easy, increase threshold slightly
                    new_adjustments[gate_type] = min(0.1, new_adjustments[gate_type] + learning_rate * 0.01)
                elif success_rate < 0.7:  # Too hard, decrease threshold slightly
                    new_adjustments[gate_type] = max(-0.1, new_adjustments[gate_type] - learning_rate * 0.01)

                # Ensure adjustments stay within reasonable bounds
                new_adjustments[gate_type] = max(-0.2, min(0.2, new_adjustments[gate_type]))

        return new_adjustments

    async def get_effective_thresholds(self, gate_type: Optional[str] = None) -> Dict[str, float]:
        """
        Get effective thresholds for all gates or a specific gate.

        Args:
            gate_type: Optional specific gate type to get threshold for

        Returns:
            Dictionary of effective thresholds
        """
        config = await self.read_current_config()

        effective_thresholds = {}
        for gate, base_threshold in config.gate_thresholds.items():
            adjustment = config.learning_adjustments.get(gate, 0.0)
            effective_threshold = max(0.0, min(1.0, base_threshold + adjustment))
            effective_thresholds[gate] = effective_threshold

        if gate_type:
            return {gate_type: effective_thresholds.get(gate_type, 0.7)}

        return effective_thresholds

    async def validate_external_input(self, input_data: Dict[str, Any]) -> bool:
        """
        Validate external service inputs for security and correctness.

        Args:
            input_data: Input data to validate

        Returns:
            True if input is valid, False otherwise
        """
        # Basic validation - can be extended based on requirements
        if not isinstance(input_data, dict):
            return False

        # Validate API key if present
        api_key = os.getenv('QUALITY_API_KEY')
        if api_key and input_data.get('api_key') != api_key:
            logger.warning("Invalid API key in external input")
            return False

        # Validate required fields for feedback data
        if 'feedback_data' in input_data:
            feedback = input_data['feedback_data']
            if not isinstance(feedback, dict):
                return False

            for gate_type, metrics in feedback.items():
                if not isinstance(metrics, dict) or 'success_rate' not in metrics:
                    return False
                if not (0 <= metrics['success_rate'] <= 1):
                    return False

        return True


# Global orchestrator instance
_orchestrator: Optional[QualityThresholdOrchestrator] = None


async def get_orchestrator() -> QualityThresholdOrchestrator:
    """Get or create global orchestrator instance."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = QualityThresholdOrchestrator()
    return _orchestrator


async def trigger_threshold_recalculation(phase: Optional[str] = None, feedback_data: Optional[Dict[str, Any]] = None) -> ThresholdConfig:
    """
    Async interface for triggering threshold recalculation.

    Args:
        phase: Optional new project phase
        feedback_data: Optional learning feedback data

    Returns:
        Updated threshold configuration

    Raises:
        OrchestratorUpdateError: If recalculation fails
    """
    orchestrator = await get_orchestrator()

    if phase:
        return await orchestrator.handle_phase_transition(phase, feedback_data)
    elif feedback_data:
        return await orchestrator.update_learning_adjustments(feedback_data)
    else:
        # Just return current config if no updates requested
        return await orchestrator.read_current_config()


if __name__ == "__main__":
    # Example usage
    async def main():
        try:
            # Initialize orchestrator
            orchestrator = QualityThresholdOrchestrator()

            # Read current configuration
            config = await orchestrator.read_current_config()
            print(f"Current phase: {config.project_phase}")
            print(f"Gate thresholds: {config.gate_thresholds}")

            # Example phase transition
            updated_config = await orchestrator.handle_phase_transition('stabilization')
            print(f"Updated phase: {updated_config.project_phase}")

            # Example learning feedback
            feedback = {
                'security': {'success_rate': 0.95},
                'code': {'success_rate': 0.85}
            }
            final_config = await orchestrator.update_learning_adjustments(feedback)
            print(f"Final adjustments: {final_config.learning_adjustments}")

        except Exception as e:
            logger.error(f"Orchestrator example failed: {e}")

    asyncio.run(main())