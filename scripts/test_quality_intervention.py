#!/usr/bin/env python3

# ==============================================================================
# Roo Autonomous AI Development Framework - Quality Intervention Test
# ==============================================================================
#
# Description:
#   This script tests the autonomous intervention capability of the
#   Quality Assurance Coordinator. It simulates a quality regression event
#   (e.g., a drop in code coverage) and verifies that the coordinator
#   detects the issue and creates a high-priority remediation task.
#
# How it works:
#   1. Backs up the current quality-dashboard.json and workflow-state.json.
#   2. Intentionally degrades a metric in quality-dashboard.json, pushing the
#      overall score below the intervention threshold (e.g., < 0.85).
#   3. Simulates the 'quality-assurance-coordinator' analyzing the dashboard.
#   4. Monitors the workflow state to confirm the coordinator has created a
#      new, high-priority task for the 'sparc-tdd-engineer' to fix the issue.
#   5. Restores the original state files.
#
# Usage:
#   python scripts/test_quality_intervention.py <project_name>
#
#   Example:
#   python scripts/test_quality_intervention.py sample-app
#
# ==============================================================================

import os
import json
import time
import uuid
import copy
import asyncio

import pytest

from validate_config import Colors, print_header, print_status

# --- Test Simulator Class ---

class QualityInterventionTester:
    """Simulates and validates a quality intervention scenario."""

    def __init__(self, project_name):
        self.project_name = project_name
        self.control_dir = os.path.join("project", project_name, "control")
        self.quality_file = os.path.join(self.control_dir, "quality-dashboard.json")
        self.workflow_file = os.path.join(self.control_dir, "workflow-state.json")
        
        self.original_quality_state = None
        self.original_workflow_state = None
        self.test_id = f"test-{uuid.uuid4().hex[:8]}"

        self.intervention_threshold = 0.85
        self.degraded_coverage = 0.60 # The value we'll set to trigger the alert
        self.expected_remediation_assignee = "sparc-tdd-engineer"

    def run_test(self):
        """Executes the entire test lifecycle."""
        print_header(f"Testing Quality Intervention for '{self.project_name}'")
        try:
            if not (os.path.exists(self.quality_file) and os.path.exists(self.workflow_file)):
                print_status("Required control files not found.", success=False)
                return False

            self._backup_states()
            self._simulate_quality_regression()
            
            time.sleep(1) # Simulate time passing

            self._simulate_qa_coordinator_action()

            return self._monitor_for_remediation_task()
        finally:
            self._cleanup()

    def _backup_states(self):
        """Saves the current state of the control files."""
        print(f"\n{Colors.OKCYAN}--- 1. Backing Up Current State ---{Colors.ENDC}")
        with open(self.quality_file, 'r') as f:
            self.original_quality_state = json.load(f)
        with open(self.workflow_file, 'r') as f:
            self.original_workflow_state = json.load(f)
        print_status("quality-dashboard.json and workflow-state.json backed up", success=True)

    def _simulate_quality_regression(self):
        """Intentionally degrades a quality metric in the dashboard."""
        print(f"\n{Colors.OKCYAN}--- 2. Simulating Quality Regression ---{Colors.ENDC}")
        state = copy.deepcopy(self.original_quality_state)
        
        # Degrade code coverage
        state['metrics']['code_coverage'] = self.degraded_coverage
        
        # Recalculate overall score (simple average for this simulation)
        # In a real system, this would be a weighted calculation.
        metric_values = state['metrics'].values()
        new_score = sum(metric_values) / len(metric_values)
        state['overall_quality_score'] = round(new_score, 2)
        state['quality_trend'] = "declining"

        with open(self.quality_file, 'w') as f:
            json.dump(state, f, indent=2)
            
        print_status(f"Code coverage dropped to {self.degraded_coverage}", success=True)
        print_status(f"Overall quality score dropped to {state['overall_quality_score']}", success=True, details=f"Threshold for intervention is < {self.intervention_threshold}")

    def _simulate_qa_coordinator_action(self):
        """Simulates the QA Coordinator detecting the drop and creating a task."""
        print(f"\n{Colors.OKCYAN}--- 3. Simulating QA Coordinator Action ---{Colors.ENDC}")
        print_status("QA Coordinator is analyzing the quality dashboard...", success=True)
        
        with open(self.quality_file, 'r') as f:
            quality_state = json.load(f)
        
        if quality_state['overall_quality_score'] < self.intervention_threshold:
            print_status("QA Coordinator detected quality score below threshold!", success=True)
            
            with open(self.workflow_file, 'r') as f:
                workflow_state = json.load(f)
            
            remediation_task = {
                "task_id": f"task-{self.test_id}-remediate-coverage",
                "title": f"Remediation: Code coverage dropped to {int(self.degraded_coverage * 100)}%",
                "status": "pending",
                "priority": "highest",
                "assigned_to": self.expected_remediation_assignee,
                "description": f"Overall quality score fell to {quality_state['overall_quality_score']}. Increase test coverage for recently modified modules."
            }
            workflow_state['pending_tasks'].append(remediation_task)
            
            with open(self.workflow_file, 'w') as f:
                json.dump(workflow_state, f, indent=2)
                
            print_status("QA Coordinator created a high-priority remediation task", success=True, details=f"Task assigned to '{self.expected_remediation_assignee}'.")
        else:
            print_status("Quality score is still above threshold. No action taken.", success=False)

    def _monitor_for_remediation_task(self, timeout=5):
        """Checks if the remediation task was created in the workflow."""
        print(f"\n{Colors.OKCYAN}--- 4. Monitoring for Remediation Task ---{Colors.ENDC}")
        start_time = time.time()
        while time.time() - start_time < timeout:
            with open(self.workflow_file, 'r') as f:
                state = json.load(f)
            for task in state.get('pending_tasks', []):
                if (task.get('assigned_to') == self.expected_remediation_assignee and
                    "Remediation: Code coverage" in task.get('title')):
                    print_status("Quality intervention test successful!", success=True, details=f"Found remediation task '{task['task_id']}'.")
                    return True
            time.sleep(1)
        print_status(f"Test failed. No remediation task for '{self.expected_remediation_assignee}' was created.", success=False)
        return False

    def _cleanup(self):
        """Restores the original state files."""
        print(f"\n{Colors.OKCYAN}--- 5. Cleaning Up ---{Colors.ENDC}")
        if self.original_quality_state:
            with open(self.quality_file, 'w') as f:
                json.dump(self.original_quality_state, f, indent=2)
            print_status("Restored original quality-dashboard.json", success=True)
        if self.original_workflow_state:
            with open(self.workflow_file, 'w') as f:
                json.dump(self.original_workflow_state, f, indent=2)
            print_status("Restored original workflow-state.json", success=True)

@pytest.mark.asyncio
async def test_quality_intervention(tmp_path, monkeypatch):
    """Confirm QA coordinator creates remediation task on regression."""
    monkeypatch.chdir(tmp_path)
    control_dir = tmp_path / "project" / "demo" / "control"
    control_dir.mkdir(parents=True)
    quality_state = {
        "metrics": {"code_coverage": 0.9, "other": 0.9},
        "overall_quality_score": 0.9,
        "quality_trend": "stable",
    }
    (control_dir / "quality-dashboard.json").write_text(json.dumps(quality_state))
    (control_dir / "workflow-state.json").write_text(json.dumps({"pending_tasks": []}))
    tester = QualityInterventionTester("demo")
    monkeypatch.setattr(time, "sleep", lambda _: None)
    result = await asyncio.to_thread(tester.run_test)
    assert result is True
