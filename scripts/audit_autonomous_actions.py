#!/usr/bin/env python3

# ==============================================================================
# Roo Autonomous AI Development Framework - Autonomous Actions Auditor
# ==============================================================================
#
# Description:
#   This script audits the logs of an autonomous project to detect anomalies
#   that may require human review. It helps identify inefficiencies, loops, or
#   systemic issues that might not be obvious from a standard progress report.
#
# Anomaly Checks Performed:
#   1. High Intervention Rate: Checks if oversight agents (QA, Tech Debt) are
#      creating an excessive number of tasks.
#   2. Task Loops/Churn: Detects if tasks with similar titles are being
#      repeatedly created, suggesting a failure loop.
#
# Usage:
#   python scripts/audit_autonomous_actions.py <project_name>
#
#   Example:
#   python scripts/audit_autonomous_actions.py sample-app
#
# ==============================================================================

import asyncio
import os
import sys
import json
import argparse
from collections import Counter
from typing import Any, Dict, List

import aiofiles

from path_utils import InvalidProjectPathError, resolve_project_path
from validate_config import Colors, print_header


class AuditError(Exception):
    """Raised when an audit operation fails."""

# --- Auditor Class ---

class ActionsAuditor:
    """Scans project logs for anomalies and generates a report."""

    def __init__(
        self,
        project_name: str,
        intervention_threshold: int = 3,
        loop_threshold: int = 2,
    ) -> None:
        self.project_name = project_name
        self.control_dir = os.path.join("project", project_name, "control")
        self.workflow_file = os.path.join(self.control_dir, "workflow-state.json")
        self.anomalies: List[Dict[str, Any]] = []

        # --- Thresholds for anomaly detection ---
        self.INTERVENTION_THRESHOLD = intervention_threshold  # Max tasks from one oversight agent
        self.LOOP_THRESHOLD = loop_threshold  # Max times a similar task can be created

    async def run_audit(self) -> None:
        """Loads data, runs all checks, and prints the final report."""
        print_header(f"Auditing Autonomous Actions for '{self.project_name}'")
        try:
            async with aiofiles.open(self.workflow_file, "r", encoding="utf-8") as f:
                content = await f.read()
            workflow_data = json.loads(content)
        except FileNotFoundError as e:
            raise AuditError("workflow-state.json not found") from e
        except json.JSONDecodeError as e:
            raise AuditError("workflow-state.json contains invalid JSON") from e

        all_tasks = (
            workflow_data.get("pending_tasks", [])
            + workflow_data.get("active_tasks", [])
            + workflow_data.get("completed_tasks", [])
        )

        if not all_tasks:
            print(
                f"{Colors.OKGREEN}No tasks found to audit. System is clean.{Colors.ENDC}"
            )
            return

        self._check_high_intervention_rate(all_tasks)
        self._check_task_loops(all_tasks)

        self._print_report()

    def _check_high_intervention_rate(self, all_tasks: List[Dict[str, Any]]) -> None:
        """Checks for an excessive number of tasks created by oversight agents."""
        oversight_agents = ["quality-assurance-coordinator", "technical-debt-manager"]
        intervention_tasks = [
            task for task in all_tasks
            if task.get('assigned_to') in oversight_agents or
               "Remediation:" in task.get('title', '')
        ]

        creator_counts = Counter(task.get('assigned_to') for task in intervention_tasks)

        for agent, count in creator_counts.items():
            if count > self.INTERVENTION_THRESHOLD:
                self.anomalies.append(
                    {
                        "type": "High Intervention Rate",
                        "details": (
                            f"Agent '{agent}' has created {count} intervention tasks, "
                            f"exceeding the threshold of {self.INTERVENTION_THRESHOLD}."
                        ),
                        "recommendation": (
                            "Review this agent's tasks to identify a potential root cause "
                            "for repeated quality/debt issues."
                        ),
                    }
                )

    def _check_task_loops(self, all_tasks: List[Dict[str, Any]]) -> None:
        """Checks for tasks with similar titles being created multiple times."""
        # Normalize titles to catch simple loops (e.g., ignoring UUIDs)
        normalized_titles = []
        for task in all_tasks:
            title = task.get('title', '').lower()
            # A simple normalization: remove "remediation:", ids, etc.
            normalized = ' '.join(title.replace('remediation:', '').split()[:4])
            normalized_titles.append(normalized)
            
        title_counts = Counter(normalized_titles)
        
        for title, count in title_counts.items():
            if count > self.LOOP_THRESHOLD:
                self.anomalies.append({
                    "type": "Potential Task Loop",
                    "details": f"A task with a title similar to '{title}...' has been created {count} times, exceeding the threshold of {self.LOOP_THRESHOLD}.",
                    "recommendation": "Investigate why this task is being repeatedly created. It may indicate a persistent failure or a logical loop in the workflow."
                })

    def _print_report(self) -> None:
        """Formats and prints the audit findings."""
        print(f"\n{Colors.OKBLUE}{Colors.UNDERLINE}Audit Summary:{Colors.ENDC}")
        if not self.anomalies:
            print(f"  {Colors.OKGREEN}✅ No anomalies detected. System operations appear normal.{Colors.ENDC}")
        else:
            print(f"  {Colors.WARNING}⚠️ Found {len(self.anomalies)} potential anomal{'y' if len(self.anomalies) == 1 else 'ies'}. Human review recommended.{Colors.ENDC}")
            for i, anomaly in enumerate(self.anomalies, 1):
                print(f"\n  --- Anomaly #{i} ---")
                print(f"  {Colors.FAIL}{Colors.BOLD}Type:{Colors.ENDC} {anomaly['type']}")
                print(f"  {Colors.BOLD}Details:{Colors.ENDC} {anomaly['details']}")
                print(f"  {Colors.OKCYAN}{Colors.BOLD}Recommendation:{Colors.ENDC} {anomaly['recommendation']}")
        
        print(f"\n{Colors.HEADER}{Colors.BOLD}===================== End of Audit ====================={Colors.ENDC}\n")

# --- Main Execution ---

async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Audit the autonomous actions for a Roo project to find anomalies.",
    )
    parser.add_argument(
        "project_name",
        type=str,
        help="The name of the project directory inside the 'project/' folder.",
    )
    args = parser.parse_args()

    try:
        project_name = await resolve_project_path(args.project_name)
    except InvalidProjectPathError as e:
        print(f"{Colors.FAIL}❌ {e}{Colors.ENDC}")
        sys.exit(1)

    auditor = ActionsAuditor(project_name)
    try:
        await auditor.run_audit()
    except AuditError as e:
        print(f"{Colors.FAIL}❌ {e}{Colors.ENDC}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
