#!/usr/bin/env python3

# ==============================================================================
# Roo Autonomous AI Development Framework - Sprint Report Generator
# ==============================================================================
#
# Description:
#   This script generates a human-readable summary of the current sprint's
#   progress. It parses data from the workflow state, quality dashboard,
#   sprint plan, and the decision log to provide a holistic overview for
#   human oversight.
#
# Usage:
#   python scripts/generate_sprint_report.py <project_name>
#
#   Example:
#   python scripts/generate_sprint_report.py sample-app
#
# Dependencies:
#   - PyYAML (pip install PyYAML)
#
# ==============================================================================

import os
import sys
import json
import yaml
import argparse
import asyncio
from datetime import datetime
from typing import Any, Dict

import aiofiles

from path_utils import InvalidProjectPathError, resolve_project_path
from validate_config import Colors


class ReportGenerationError(Exception):
    """Raised when generating the sprint report fails."""

# --- Report Generator Class ---

class ReportGenerator:
    """Parses project files and generates a formatted sprint report."""

    def __init__(self, project_name: str) -> None:
        self.project_name = project_name
        self.control_dir = os.path.join("project", project_name, "control")
        self.memory_dir = "memory-bank"
        self.data: Dict[str, Any] = {}

    async def generate_report(self) -> None:
        """Loads data, processes it, and prints the final report."""
        await self._load_data()
        self._print_report()

    async def _load_data(self) -> None:
        """Loads all necessary files into the data dictionary."""
        print(
            f"{Colors.OKCYAN}--- Loading data for project '{self.project_name}'... ---{Colors.ENDC}"
        )
        try:
            async with aiofiles.open(
                os.path.join(self.control_dir, "sprint.yaml"),
                "r",
                encoding="utf-8",
            ) as f:
                sprint_content = await f.read()
            self.data["sprint"] = yaml.safe_load(sprint_content)

            async with aiofiles.open(
                os.path.join(self.control_dir, "workflow-state.json"),
                "r",
                encoding="utf-8",
            ) as f:
                workflow_content = await f.read()
            self.data["workflow"] = json.loads(workflow_content)

            async with aiofiles.open(
                os.path.join(self.control_dir, "quality-dashboard.json"),
                "r",
                encoding="utf-8",
            ) as f:
                quality_content = await f.read()
            self.data["quality"] = json.loads(quality_content)

            async with aiofiles.open(
                os.path.join(self.memory_dir, "decisionLog.md"),
                "r",
                encoding="utf-8",
            ) as f:
                lines = [
                    line.strip()
                    for line in await f.readlines()
                    if line.strip() and not line.startswith("#")
                ]
            self.data["decisions"] = lines[-5:]
        except FileNotFoundError as e:
            raise ReportGenerationError(f"Missing file: {e.filename}") from e
        except (yaml.YAMLError, json.JSONDecodeError) as e:
            raise ReportGenerationError(f"Failed to parse project data: {e}") from e

    def _print_report(self) -> None:
        """Formats and prints the loaded data to the console."""
        sprint_info = self.data['sprint']
        workflow = self.data['workflow']
        quality = self.data['quality']
        decisions = self.data['decisions']

        # --- Header ---
        print(f"\n{Colors.HEADER}{Colors.BOLD}======================================================={Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}  Sprint Report: {sprint_info.get('sprint_id', 'N/A')}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}  Project: {self.project_name}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}  Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}======================================================={Colors.ENDC}")

        # --- Sprint Goal ---
        print(f"\n{Colors.OKBLUE}{Colors.UNDERLINE}Sprint Goal:{Colors.ENDC}")
        print(f"  {sprint_info.get('goal', 'No goal defined.')}")

        # --- Progress Summary ---
        completed = len(workflow.get('completed_tasks', []))
        active = len(workflow.get('active_tasks', []))
        pending = len(workflow.get('pending_tasks', []))
        total = completed + active + pending
        progress_percent = (completed / total * 100) if total > 0 else 0

        print(f"\n{Colors.OKBLUE}{Colors.UNDERLINE}Progress & Velocity:{Colors.ENDC}")
        print(f"  - {Colors.BOLD}Tasks Completed:{Colors.ENDC} {completed} / {total} ({progress_percent:.1f}%)")
        print(f"  - {Colors.BOLD}Tasks Active:{Colors.ENDC}    {active}")
        print(f"  - {Colors.BOLD}Tasks Pending:{Colors.ENDC}   {pending}")
        print(f"  - {Colors.BOLD}Development Velocity:{Colors.ENDC} {completed} tasks completed this sprint.")

        # --- Quality Dashboard ---
        score = quality.get('overall_quality_score', 0)
        trend = quality.get('quality_trend', 'N/A')
        trend_color = Colors.OKGREEN if trend == 'stable' or trend == 'improving' else Colors.FAIL

        print(f"\n{Colors.OKBLUE}{Colors.UNDERLINE}Quality Dashboard:{Colors.ENDC}")
        print(f"  - {Colors.BOLD}Overall Quality Score:{Colors.ENDC} {score * 100:.1f}%")
        print(f"  - {Colors.BOLD}Quality Trend:{Colors.ENDC} {trend_color}{trend.capitalize()}{Colors.ENDC}")
        print(f"  - {Colors.BOLD}Metrics:{Colors.ENDC}")
        for key, value in quality.get('metrics', {}).items():
            metric_name = key.replace('_', ' ').capitalize()
            # Format as percentage if it's a ratio/coverage
            display_value = f"{value * 100:.1f}%" if 'ratio' in key or 'coverage' in key or 'rate' in key else value
            print(f"    - {metric_name}: {display_value}")

        # --- Key Autonomous Decisions ---
        print(f"\n{Colors.OKBLUE}{Colors.UNDERLINE}Recent Autonomous Decisions (from decisionLog.md):{Colors.ENDC}")
        if decisions:
            for decision in decisions:
                if decision != "---":
                    print(f"  - {decision}")
        else:
            print("  No recent decisions logged.")

        print(f"\n{Colors.HEADER}{Colors.BOLD}===================== End of Report ====================={Colors.ENDC}\n")


# --- Main Execution ---

async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a sprint progress report for a Roo project.",
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

    reporter = ReportGenerator(project_name)
    try:
        await reporter.generate_report()
    except ReportGenerationError as e:
        print(f"{Colors.FAIL}❌ {e}{Colors.ENDC}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
