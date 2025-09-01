#!/usr/bin/env python3

# ==============================================================================
# Roo Autonomous AI Development Framework - Configuration Validator
# ==============================================================================
#
# Description:
#   This script validates all critical configuration files for a specified
#   Roo project. It ensures that files exist, are correctly formatted, and
#   adhere to the framework's contracts (schemas). This prevents the
#   autonomous system from starting in an invalid state.
#
# Dependencies:
#   - PyYAML (pip install PyYAML)
#   - jsonschema (pip install jsonschema)
#
# Usage:
#   python scripts/validate_config.py <project_name>
#
#   Example:
#   python scripts/validate_config.py sample-app
#
# ==============================================================================

import os
import sys
import json
import yaml
import argparse
import asyncio
from jsonschema import validate, ValidationError

from path_utils import InvalidProjectPathError, resolve_project_path


class ConfigValidationError(Exception):
    """Raised when configuration validation encounters a file or parsing error."""

# --- ANSI Color Codes for Better Output ---
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# --- Helper Functions ---

def print_header(message: str) -> None:
    """Prints a formatted header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}================================================={Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}  {message}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}================================================={Colors.ENDC}")

def print_status(message: str, success: bool = True, details: str = "") -> None:
    """Prints a status message with a checkmark or cross."""
    if success:
        print(f"  {Colors.OKGREEN}✅ {message}{Colors.ENDC}")
    else:
        print(f"  {Colors.FAIL}❌ {message}{Colors.ENDC}")
    if details:
        print(f"     {Colors.OKCYAN}{details}{Colors.ENDC}")

def print_error(message, details=""):
    """Prints a formatted error message."""
    print(f"    {Colors.FAIL}Error: {message}{Colors.ENDC}")
    if details:
        # Indent details for readability
        indented_details = "\n".join(["      " + line for line in str(details).splitlines()])
        print(f"{Colors.WARNING}{indented_details}{Colors.ENDC}")


# --- Validator Class ---

class ConfigValidator:
    """A class to encapsulate the validation logic for a Roo project."""

    def __init__(self, project_name):
        self.project_name = project_name
        self.project_dir = os.path.join("project", project_name)
        self.control_dir = os.path.join(self.project_dir, "control")
        self.schema_dir = os.path.join("docs", "contracts")
        self.errors = 0

    def run_validations(self):
        """Runs all validation checks and returns the final status."""
        print_header(f"Validating Project: {self.project_name}")

        self._validate_file_existence()
        # Stop if core files are missing, as other checks will fail
        if self.errors > 0:
            return False

        self._validate_roomodes()
        self._validate_yaml_files()
        self._validate_json_files()
        self._cross_reference_capabilities()

        return self.errors == 0

    def _check_path(self, path, is_dir=False):
        """Helper to check if a file or directory exists."""
        check = os.path.isdir if is_dir else os.path.isfile
        if not check(path):
            self.errors += 1
            print_status(f"Checking path: {path}", success=False)
            print_error(f"{'Directory' if is_dir else 'File'} not found.")
            return False
        print_status(f"Checking path: {path}", success=True)
        return True

    def _validate_file_existence(self):
        """Checks that all required files and directories exist."""
        print(f"\n{Colors.OKCYAN}--- 1. Validating File & Directory Structure ---{Colors.ENDC}")
        self._check_path(".roomodes")
        self._check_path(self.project_dir, is_dir=True)
        self._check_path(self.control_dir, is_dir=True)
        self._check_path(self.schema_dir, is_dir=True)
        
        # Check control files
        for f in ["backlog.yaml", "sprint.yaml", "capabilities.yaml", "workflow-state.json", "quality-dashboard.json"]:
            self._check_path(os.path.join(self.control_dir, f))
            
        # Check schema files
        for s in ["backlog_v1.schema.json", "workflow_state_v2.schema.json"]:
            self._check_path(os.path.join(self.schema_dir, s))

    def _validate_roomodes(self):
        """Validates the format of the .roomodes file."""
        print(f"\n{Colors.OKCYAN}--- 2. Validating .roomodes File ---{Colors.ENDC}")
        path = ".roomodes"
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except OSError as e:
            raise ConfigValidationError(f"Could not read {path}") from e
        if not content.strip():
            self.errors += 1
            print_status("Checking .roomodes content", success=False)
            print_error("File is empty.")
        else:
            print_status("Checking .roomodes content", success=True)

    def _validate_yaml_files(self):
        """Parses and validates the structure of YAML files."""
        print(f"\n{Colors.OKCYAN}--- 3. Validating YAML Files ---{Colors.ENDC}")
        # --- capabilities.yaml ---
        path = os.path.join(self.control_dir, "capabilities.yaml")
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except FileNotFoundError as e:
            raise ConfigValidationError(f"Missing file: {path}") from e
        except yaml.YAMLError as e:
            raise ConfigValidationError(f"YAML syntax error in {path}: {e}") from e
        if "agents" in data and isinstance(data["agents"], list) and data["agents"]:
            print_status("Validating capabilities.yaml structure", success=True)
        else:
            self.errors += 1
            print_status("Validating capabilities.yaml structure", success=False)
            print_error("Must contain a non-empty list under the 'agents' key.")

        # --- sprint.yaml ---
        path = os.path.join(self.control_dir, "sprint.yaml")
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except FileNotFoundError as e:
            raise ConfigValidationError(f"Missing file: {path}") from e
        except yaml.YAMLError as e:
            raise ConfigValidationError(f"YAML syntax error in {path}: {e}") from e
        required_keys = ["sprint_id", "goal", "status"]
        missing_keys = [key for key in required_keys if key not in data]
        if not missing_keys:
            print_status("Validating sprint.yaml structure", success=True)
        else:
            self.errors += 1
            print_status("Validating sprint.yaml structure", success=False)
            print_error(f"Missing required keys: {', '.join(missing_keys)}")

    def _validate_json_files(self):
        """Validates JSON files against their defined schemas."""
        print(f"\n{Colors.OKCYAN}--- 4. Validating JSON Files Against Schemas ---{Colors.ENDC}")
        
        validation_map = {
            "workflow-state.json": "workflow_state_v2.schema.json",
            # Add other JSON/schema mappings here
        }

        for data_file, schema_file in validation_map.items():
            data_path = os.path.join(self.control_dir, data_file)
            schema_path = os.path.join(self.schema_dir, schema_file)

            try:
                with open(data_path, "r", encoding="utf-8") as f:
                    data_instance = json.load(f)
                with open(schema_path, "r", encoding="utf-8") as f:
                    schema = json.load(f)
            except FileNotFoundError as e:
                raise ConfigValidationError(f"Missing file: {e.filename}") from e
            except json.JSONDecodeError as e:
                raise ConfigValidationError(f"JSON syntax error in {data_file}: {e}") from e

            try:
                validate(instance=data_instance, schema=schema)
                print_status(
                    f"Validating {data_file} against {schema_file}", success=True
                )
            except ValidationError as e:
                self.errors += 1
                print_status(
                    f"Validating {data_file} against {schema_file}", success=False
                )
                print_error("Schema validation failed.", details=e.message)

    def _cross_reference_capabilities(self):
        """Ensures agents in capabilities.yaml are defined in .roomodes."""
        print(f"\n{Colors.OKCYAN}--- 5. Cross-Referencing Agent Capabilities ---{Colors.ENDC}")
        try:
            with open(".roomodes", "r", encoding="utf-8") as f:
                defined_modes = {line.strip() for line in f if line.strip()}

            cap_path = os.path.join(self.control_dir, "capabilities.yaml")
            with open(cap_path, "r", encoding="utf-8") as f:
                project_caps = yaml.safe_load(f)
        except FileNotFoundError as e:
            raise ConfigValidationError(f"Missing file: {e.filename}") from e
        except yaml.YAMLError as e:
            raise ConfigValidationError(
                f"YAML parsing error in {cap_path}: {e}"
            ) from e
        except OSError as e:
            raise ConfigValidationError(f"Could not read file: {e.filename}") from e

        project_agents = set(project_caps.get("agents", []))
        undefined_agents = project_agents - defined_modes

        if not undefined_agents:
            print_status("All project agents are defined in .roomodes", success=True)
        else:
            self.errors += 1
            print_status("All project agents are defined in .roomodes", success=False)
            print_error(
                "The following agents in capabilities.yaml are not defined in .roomodes: "
                + ", ".join(undefined_agents)
            )


# --- Main Execution ---

async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate the configuration for a Roo Autonomous AI Framework project.",
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

    validator = ConfigValidator(project_name)
    try:
        is_valid = await asyncio.to_thread(validator.run_validations)
    except ConfigValidationError as e:
        print(f"{Colors.FAIL}❌ {e}{Colors.ENDC}")
        sys.exit(1)

    if is_valid:
        print_header("✅ Validation Successful ✅")
        print(f"{Colors.OKGREEN}All configuration files for project '{project_name}' are valid.{Colors.ENDC}")
        sys.exit(0)
    else:
        print_header("❌ Validation Failed ❌")
        print(f"{Colors.FAIL}Found {validator.errors} error(s) in the configuration for project '{project_name}'.{Colors.ENDC}")
        print(f"{Colors.WARNING}Please fix the issues listed above before starting the autonomous system.{Colors.ENDC}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
