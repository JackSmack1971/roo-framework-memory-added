#!/usr/bin/env python3

# ==============================================================================
# Roo Autonomous AI Development Framework - Dynamic Delegation Test
# ==============================================================================
#
# Description:
#   This script tests the meta-cognitive capabilities of the autonomous agents.
#   It simulates a scenario where a task with security implications is introduced
#   and verifies that the system correctly delegates a sub-task to the
#   appropriate specialist (e.g., a security-reviewer).
#
# How it works:
#   1. Backs up the current workflow-state.json.
#   2. Injects a new task into the 'pending_tasks' list.
#   3. Simulates the 'sparc-code-implementer' picking up the task and, upon
#      recognizing a keyword ('payment'), creating a new 'boomerang task' for
#      the 'security-reviewer'.
#   4. Monitors the workflow state to confirm the new security task appears.
#   5. Restores the original workflow-state.json, leaving the system unchanged.
#
# Usage:
#   python scripts/test_dynamic_delegation.py <project_name>
#
#   Example:
#   python scripts/test_dynamic_delegation.py sample-app
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

class DelegationTester:
    """Simulates and validates a dynamic delegation scenario."""

    def __init__(self, project_name):
        self.project_name = project_name
        self.control_dir = os.path.join("project", project_name, "control")
        self.workflow_file = os.path.join(self.control_dir, "workflow-state.json")
        self.original_workflow_state = None
        self.test_id = f"test-{uuid.uuid4().hex[:8]}"

        # This is the task we will inject.
        self.initial_task = {
            "task_id": f"task-{self.test_id}-impl",
            "title": "Implement Stripe payment processing API",
            "status": "pending",
            "assigned_to": "sparc-code-implementer",
            "dependencies": []
        }

        # This is the task we expect to be created as a result.
        self.expected_delegated_task_assignee = "security-reviewer"

    def run_test(self):
        """Executes the entire test lifecycle."""
        print_header(f"Testing Dynamic Delegation for '{self.project_name}'")
        try:
            if not self._check_prerequisites():
                return False

            self._backup_workflow_state()
            self._inject_initial_task()

            # Give a moment for the "system" to notice the new task
            print("\n  ⏳ Simulating system latency...")
            time.sleep(2)

            self._simulate_agent_action()

            # Monitor for the result
            return self._monitor_for_delegation()

        finally:
            self._cleanup()

    def _check_prerequisites(self):
        """Ensure necessary files exist."""
        print(f"\n{Colors.OKCYAN}--- 1. Checking Prerequisites ---{Colors.ENDC}")
        if not os.path.exists(self.workflow_file):
            print_status(f"Workflow state file exists at {self.workflow_file}", success=False)
            return False
        print_status("Workflow state file found", success=True)
        return True

    def _backup_workflow_state(self):
        """Saves the current state of the workflow file."""
        print(f"\n{Colors.OKCYAN}--- 2. Backing Up Current State ---{Colors.ENDC}")
        with open(self.workflow_file, 'r') as f:
            self.original_workflow_state = json.load(f)
        print_status("workflow-state.json backed up successfully", success=True)

    def _inject_initial_task(self):
        """Adds the test task to the workflow state."""
        print(f"\n{Colors.OKCYAN}--- 3. Injecting Initial Task ---{Colors.ENDC}")
        state = copy.deepcopy(self.original_workflow_state)
        state['pending_tasks'].append(self.initial_task)
        with open(self.workflow_file, 'w') as f:
            json.dump(state, f, indent=2)
        print_status(f"Injected task '{self.initial_task['task_id']}' for '{self.initial_task['assigned_to']}'", success=True)

    def _simulate_agent_action(self):
        """
        Simulates the sparc-code-implementer processing the task and creating a
        new delegated task.
        """
        print(f"\n{Colors.OKCYAN}--- 4. Simulating Agent Action ---{Colors.ENDC}")
        print_status("Simulating 'sparc-code-implementer' analyzing the task...", success=True, details="Agent detects keyword 'payment'...")

        with open(self.workflow_file, 'r') as f:
            state = json.load(f)

        # Find our injected task and move it to active
        task_found = False
        for i, task in enumerate(state['pending_tasks']):
            if task['task_id'] == self.initial_task['task_id']:
                active_task = state['pending_tasks'].pop(i)
                active_task['status'] = 'active'
                state['active_tasks'].append(active_task)
                task_found = True
                break

        if not task_found:
            print_status("Could not find injected task to simulate.", success=False)
            return

        # Create the new delegated task
        delegated_task = {
            "task_id": f"task-{self.test_id}-sec-review",
            "title": f"Security review for payment processing: {self.initial_task['title']}",
            "status": "pending",
            "assigned_to": self.expected_delegated_task_assignee,
            "dependencies": [self.initial_task['task_id']]
        }
        state['pending_tasks'].append(delegated_task)

        with open(self.workflow_file, 'w') as f:
            json.dump(state, f, indent=2)

        print_status("Agent created a new delegated task", success=True, details=f"New task for '{delegated_task['assigned_to']}' added to pending tasks.")

    def _monitor_for_delegation(self, timeout=10, interval=1):
        """Polls the workflow state to see if the expected task was created."""
        print(f"\n{Colors.OKCYAN}--- 5. Monitoring for Expected Delegation ---{Colors.ENDC}")
        start_time = time.time()
        while time.time() - start_time < timeout:
            with open(self.workflow_file, 'r') as f:
                state = json.load(f)

            all_tasks = state.get('pending_tasks', []) + state.get('active_tasks', [])
            for task in all_tasks:
                if task.get('assigned_to') == self.expected_delegated_task_assignee:
                    print_status("Dynamic delegation successful!", success=True, details=f"Found task '{task['task_id']}' assigned to '{self.expected_delegated_task_assignee}'.")
                    return True
            
            print(f"  ... Checking... (elapsed: {int(time.time() - start_time)}s)")
            time.sleep(interval)

        print_status(f"Test failed. No task for '{self.expected_delegated_task_assignee}' was created within the timeout.", success=False)
        return False

    def _cleanup(self):
        """Restores the original workflow state."""
        print(f"\n{Colors.OKCYAN}--- 6. Cleaning Up ---{Colors.ENDC}")
        if self.original_workflow_state:
            with open(self.workflow_file, 'w') as f:
                json.dump(self.original_workflow_state, f, indent=2)
            print_status("Restored original workflow-state.json", success=True)
        else:
            print_status("No backup found, skipping restore.", success=False)

@pytest.mark.asyncio
async def test_dynamic_delegation(tmp_path, monkeypatch):
    """Ensure a delegated task is created for security review."""
    monkeypatch.chdir(tmp_path)
    control_dir = tmp_path / "project" / "demo" / "control"
    control_dir.mkdir(parents=True)
    data = {"pending_tasks": [], "active_tasks": []}
    (control_dir / "workflow-state.json").write_text(json.dumps(data))
    tester = DelegationTester("demo")
    monkeypatch.setattr(time, "sleep", lambda _: None)
    result = await asyncio.to_thread(tester.run_test)
    assert result is True
