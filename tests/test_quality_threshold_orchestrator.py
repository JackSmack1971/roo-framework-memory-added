"""
Unit tests for QualityThresholdOrchestrator

Tests phase transitions, learning feedback integration, and threshold recalculation
with various scenarios including error conditions and edge cases.
"""

import asyncio
import json
import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import the orchestration module
import importlib.util
spec = importlib.util.spec_from_file_location(
    "orchestration.main",
    os.path.join(os.path.dirname(__file__), '..', 'src', 'orchestration', 'main.py')
)

if spec is None or spec.loader is None:
    raise ImportError("Could not load orchestration module")

orchestration_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(orchestration_module)

QualityThresholdOrchestrator = orchestration_module.QualityThresholdOrchestrator
OrchestratorUpdateError = orchestration_module.OrchestratorUpdateError
ThresholdConfig = orchestration_module.ThresholdConfig
trigger_threshold_recalculation = orchestration_module.trigger_threshold_recalculation
get_orchestrator = orchestration_module.get_orchestrator


class TestQualityThresholdOrchestrator(unittest.TestCase):
    """Test cases for QualityThresholdOrchestrator functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.dashboard_path = os.path.join(self.temp_dir, 'test-dashboard.json')

        # Create initial dashboard configuration
        self.initial_config = {
            "schema": "QUALITY_DASHBOARD/V2",
            "project_id": "test-project",
            "project_phase": "dev",
            "gate_thresholds": {
                "security": 0.8,
                "performance": 0.75,
                "code": 0.7,
                "architecture": 0.8,
                "general": 0.7,
                "api_documentation": 0.75,
                "code_documentation": 0.7,
                "architecture_documentation": 0.8,
                "usage_documentation": 0.7
            },
            "learning_adjustments": {
                "security": 0.0,
                "performance": 0.0,
                "code": 0.0,
                "architecture": 0.0,
                "general": 0.0,
                "api_documentation": 0.0,
                "code_documentation": 0.0,
                "architecture_documentation": 0.0,
                "usage_documentation": 0.0
            },
            "updated_at": "2025-08-29T00:00:00Z"
        }

        # Write initial config to file
        with open(self.dashboard_path, 'w') as f:
            json.dump(self.initial_config, f, indent=2)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_initialization_success(self):
        """Test successful orchestrator initialization."""
        orchestrator = QualityThresholdOrchestrator(self.dashboard_path)
        self.assertEqual(orchestrator.dashboard_path, self.dashboard_path)
        self.assertEqual(orchestrator.timeout_ms, 5000)

    def test_initialization_missing_path(self):
        """Test initialization failure with missing dashboard path."""
        with self.assertRaises(ValueError):
            QualityThresholdOrchestrator(None)

    @patch.dict(os.environ, {}, clear=True)
    def test_initialization_missing_env_var(self):
        """Test initialization failure with missing environment variable."""
        with self.assertRaises(ValueError):
            QualityThresholdOrchestrator()

    async def test_read_current_config_success(self):
        """Test successful configuration reading."""
        orchestrator = QualityThresholdOrchestrator(self.dashboard_path)
        config = await orchestrator.read_current_config()

        self.assertEqual(config.project_phase, "dev")
        self.assertEqual(config.gate_thresholds["security"], 0.8)
        self.assertEqual(config.learning_adjustments["security"], 0.0)

    async def test_read_current_config_invalid_json(self):
        """Test configuration reading with invalid JSON."""
        # Write invalid JSON
        with open(self.dashboard_path, 'w') as f:
            f.write("invalid json content")

        orchestrator = QualityThresholdOrchestrator(self.dashboard_path)

        with self.assertRaises(OrchestratorUpdateError):
            await orchestrator.read_current_config()

    async def test_read_current_config_missing_fields(self):
        """Test configuration reading with missing required fields."""
        invalid_config = {"schema": "QUALITY_DASHBOARD/V2"}  # Missing required fields

        with open(self.dashboard_path, 'w') as f:
            json.dump(invalid_config, f)

        orchestrator = QualityThresholdOrchestrator(self.dashboard_path)

        with self.assertRaises(OrchestratorUpdateError):
            await orchestrator.read_current_config()

    async def test_phase_transition_success(self):
        """Test successful phase transition."""
        orchestrator = QualityThresholdOrchestrator(self.dashboard_path)

        # Transition to stabilization phase
        updated_config = await orchestrator.handle_phase_transition("stabilization")

        self.assertEqual(updated_config.project_phase, "stabilization")
        # Security threshold should be adjusted by phase multiplier (1.0 for stabilization)
        self.assertEqual(updated_config.gate_thresholds["security"], 0.8)  # 0.8 * 1.0

    async def test_phase_transition_invalid_phase(self):
        """Test phase transition with invalid phase."""
        orchestrator = QualityThresholdOrchestrator(self.dashboard_path)

        with self.assertRaises(OrchestratorUpdateError):
            await orchestrator.handle_phase_transition("invalid_phase")

    async def test_phase_transition_with_feedback(self):
        """Test phase transition with learning feedback."""
        orchestrator = QualityThresholdOrchestrator(self.dashboard_path)

        feedback_data = {
            "security": {"success_rate": 0.95},  # High success, should increase threshold slightly
            "code": {"success_rate": 0.6}       # Low success, should decrease threshold slightly
        }

        updated_config = await orchestrator.handle_phase_transition("stabilization", feedback_data)

        self.assertEqual(updated_config.project_phase, "stabilization")
        # Learning adjustments should be applied
        self.assertGreater(updated_config.learning_adjustments["security"], 0.0)
        self.assertLess(updated_config.learning_adjustments["code"], 0.0)

    async def test_learning_adjustments_update(self):
        """Test learning adjustments update."""
        orchestrator = QualityThresholdOrchestrator(self.dashboard_path)

        feedback_data = {
            "performance": {"success_rate": 0.9},  # Should trigger slight increase
            "architecture": {"success_rate": 0.65} # Should trigger slight decrease
        }

        updated_config = await orchestrator.update_learning_adjustments(feedback_data)

        # Check that adjustments were applied
        self.assertNotEqual(updated_config.learning_adjustments["performance"], 0.0)
        self.assertNotEqual(updated_config.learning_adjustments["architecture"], 0.0)

    async def test_get_effective_thresholds(self):
        """Test effective thresholds calculation."""
        orchestrator = QualityThresholdOrchestrator(self.dashboard_path)

        # First update learning adjustments
        feedback_data = {"security": {"success_rate": 0.95}}
        await orchestrator.update_learning_adjustments(feedback_data)

        # Get effective thresholds
        effective = await orchestrator.get_effective_thresholds()

        # Security threshold should be adjusted
        self.assertGreater(effective["security"], 0.8)  # Base 0.8 + positive adjustment

    async def test_get_effective_thresholds_specific_gate(self):
        """Test effective thresholds for specific gate."""
        orchestrator = QualityThresholdOrchestrator(self.dashboard_path)

        effective = await orchestrator.get_effective_thresholds("security")

        self.assertIn("security", effective)
        self.assertEqual(len(effective), 1)

    async def test_validate_external_input_valid(self):
        """Test validation of valid external input."""
        orchestrator = QualityThresholdOrchestrator(self.dashboard_path)

        valid_input = {
            "feedback_data": {
                "security": {"success_rate": 0.85},
                "code": {"success_rate": 0.75}
            }
        }

        is_valid = await orchestrator.validate_external_input(valid_input)
        self.assertTrue(is_valid)

    async def test_validate_external_input_invalid_structure(self):
        """Test validation of invalid external input structure."""
        orchestrator = QualityThresholdOrchestrator(self.dashboard_path)

        invalid_inputs = [
            "not_a_dict",
            {"feedback_data": "not_a_dict"},
            {"feedback_data": {"security": "not_a_dict"}},
            {"feedback_data": {"security": {"success_rate": 1.5}}},  # Invalid success rate
        ]

        for invalid_input in invalid_inputs:
            is_valid = await orchestrator.validate_external_input(invalid_input)
            self.assertFalse(is_valid, f"Input should be invalid: {invalid_input}")

    async def test_write_config_success(self):
        """Test successful configuration writing."""
        orchestrator = QualityThresholdOrchestrator(self.dashboard_path)

        new_config = ThresholdConfig(
            project_phase="release",
            gate_thresholds={
                "security": 0.9, "code": 0.8, "performance": 0.85, "architecture": 0.9, "general": 0.8,
                "api_documentation": 0.85, "code_documentation": 0.8, "architecture_documentation": 0.9, "usage_documentation": 0.8
            },
            learning_adjustments={
                "security": 0.05, "code": -0.02, "performance": 0.03, "architecture": 0.02, "general": 0.01,
                "api_documentation": 0.03, "code_documentation": -0.01, "architecture_documentation": 0.02, "usage_documentation": 0.01
            },
            updated_at="2025-08-29T01:00:00Z"
        )

        await orchestrator.write_config(new_config)

        # Verify file was updated
        with open(self.dashboard_path, 'r') as f:
            updated_data = json.load(f)

        self.assertEqual(updated_data["project_phase"], "release")
        self.assertEqual(updated_data["gate_thresholds"]["security"], 0.9)

    async def test_trigger_threshold_recalculation_phase_only(self):
        """Test global trigger function with phase only."""
        with patch.dict(os.environ, {'QUALITY_DASHBOARD_PATH': self.dashboard_path}):
            config = await trigger_threshold_recalculation(phase="stabilization")

            self.assertEqual(config.project_phase, "stabilization")

    async def test_trigger_threshold_recalculation_feedback_only(self):
        """Test global trigger function with feedback only."""
        with patch.dict(os.environ, {'QUALITY_DASHBOARD_PATH': self.dashboard_path}):
            feedback = {"security": {"success_rate": 0.9}}
            config = await trigger_threshold_recalculation(feedback_data=feedback)

            # Should have applied learning adjustments
            self.assertNotEqual(config.learning_adjustments["security"], 0.0)

    async def test_trigger_threshold_recalculation_both(self):
        """Test global trigger function with both phase and feedback."""
        with patch.dict(os.environ, {'QUALITY_DASHBOARD_PATH': self.dashboard_path}):
            feedback = {"code": {"success_rate": 0.8}}
            config = await trigger_threshold_recalculation(phase="release", feedback_data=feedback)

            self.assertEqual(config.project_phase, "release")
            self.assertNotEqual(config.learning_adjustments["code"], 0.0)

    async def test_get_orchestrator_singleton(self):
        """Test orchestrator singleton pattern."""
        with patch.dict(os.environ, {'QUALITY_DASHBOARD_PATH': self.dashboard_path}):
            orch1 = await get_orchestrator()
            orch2 = await get_orchestrator()

            self.assertIs(orch1, orch2)  # Should be same instance

    async def test_retry_mechanism(self):
        """Test retry mechanism for file operations."""
        orchestrator = QualityThresholdOrchestrator(self.dashboard_path)

        # Mock file operation to fail twice then succeed
        original_read = orchestrator.read_current_config

        async def mock_read(retries=3):
            if not hasattr(mock_read, 'call_count'):
                mock_read.call_count = 0
            mock_read.call_count += 1

            if mock_read.call_count < 3:
                raise FileNotFoundError("Mock file not found")

            return await original_read()

        orchestrator.read_current_config = mock_read

        # Should succeed on third attempt
        config = await orchestrator.read_current_config(retries=3)
        self.assertIsInstance(config, ThresholdConfig)


if __name__ == '__main__':
    # Run async tests
    async def run_async_tests():
        """Run all async test methods."""
        test_instance = TestQualityThresholdOrchestrator()
        test_instance.setUp()

        test_methods = [
            method for method in dir(test_instance)
            if method.startswith('test_') and asyncio.iscoroutinefunction(getattr(test_instance, method))
        ]

        for method_name in test_methods:
            print(f"Running {method_name}...")
            try:
                await getattr(test_instance, method_name)()
                print(f"✅ {method_name} passed")
            except Exception as e:
                print(f"❌ {method_name} failed: {e}")
                raise
            finally:
                test_instance.tearDown()

    # Run sync tests normally
    unittest.main(argv=[''], exit=False, verbosity=2)

    # Run async tests
    print("\nRunning async tests...")
    asyncio.run(run_async_tests())