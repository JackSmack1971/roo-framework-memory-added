#!/bin/bash

# ==============================================================================
# Roo Autonomous AI Development Framework - Project Setup Script
# ==============================================================================
#
# Description:
#   This master script automates the initial setup for a new project within
#   the Roo framework, as outlined in the implementation_guide.md. It creates
#   the necessary directory structure, initializes control files with default
#   values, and sets up the memory bank for the autonomous agents.
#
# Usage:
#   ./setup_project.sh
#
# ==============================================================================

# --- Configuration ---
# Exit immediately if a command exits with a non-zero status.
set -e

# --- Helper Functions ---

# Function to print a formatted header message.
print_header() {
  echo ""
  echo "================================================="
  echo "  $1"
  echo "================================================="
}

# Function to print a success message for a step.
print_success() {
  echo "✅  $1"
}

# --- Intelligent Project Analysis Functions ---

# Function to analyze project requirements and suggest optimal configuration
analyze_project_intelligence() {
    echo "🧠 Analyzing project requirements for optimal autonomous configuration..."

    # Create new control plane files with intelligent defaults
    touch "project/$PROJECT_NAME/control/capabilities.yaml"
    touch "project/$PROJECT_NAME/control/issue-patterns.yaml"
    touch "project/$PROJECT_NAME/control/workflow-state.json"
    touch "project/$PROJECT_NAME/control/quality-dashboard.json"
    touch "project/$PROJECT_NAME/control/technical-debt-register.json"
    touch "project/$PROJECT_NAME/control/orchestrator-decisions.log.jsonl"

    # Add new memory bank files within project structure
    touch "project/memory-bank/learningHistory.md"
    touch "project/memory-bank/delegationPatterns.md"
    touch "project/memory-bank/conflictResolutions.md"
    touch "project/memory-bank/qualityMetrics.md"
    touch "project/memory-bank/technicalDebt.md"
    touch "project/memory-bank/autonomousInsights.md"

    print_success "Intelligent control plane initialized"
}

# Function to configure intelligent circuit breakers based on project size
configure_intelligent_circuit_breakers() {
    echo "🔧 Configuring intelligent circuit breakers..."

    # Update JSON file paths in functions with intelligent defaults
    jq '.circuit_breaker_states.infinite_delegation_prevention.max_delegation_depth = 6' \
       "project/$PROJECT_NAME/control/workflow-state.json" > temp.json && mv temp.json "project/$PROJECT_NAME/control/workflow-state.json"

    jq '.circuit_breaker_states.resource_contention_management.concurrent_task_limit = 12' \
       "project/$PROJECT_NAME/control/workflow-state.json" > temp.json && mv temp.json "project/$PROJECT_NAME/control/workflow-state.json"

    print_success "Circuit breakers configured with intelligent thresholds"
}

# Function to initialize quality optimization settings
initialize_quality_intelligence() {
    echo "📊 Initializing quality intelligence dashboard..."

    # Update quality dashboard path with intelligent defaults
    jq '.intelligent_analysis.velocity_quality_optimization.optimal_quality_speed_balance = 0.95' \
       "project/$PROJECT_NAME/control/quality-dashboard.json" > temp.json && mv temp.json "project/$PROJECT_NAME/control/quality-dashboard.json"

    print_success "Quality intelligence initialized"
}

# --- Main Script ---

print_header "Roo Framework Project Initialization with Intelligence"

# 1. Get Project Name from User
read -p "Enter a name for the new project (e.g., 'new-mobile-app'): " PROJECT_NAME

if [ -z "$PROJECT_NAME" ]; then
  echo "❌ Error: Project name cannot be empty."
  exit 1
fi

if [ -d "project/$PROJECT_NAME" ]; then
  echo "❌ Error: A project named '$PROJECT_NAME' already exists."
  exit 1
fi

echo "🚀  Starting setup for project: $PROJECT_NAME"

# 2. Create Core Project Directories
print_header "Step 1: Creating Directory Structure"
mkdir -p "project/$PROJECT_NAME/control"
mkdir -p "project/$PROJECT_NAME/src"
mkdir -p "memory-bank" # Ensures memory-bank exists at the root
print_success "Project directories created at project/$PROJECT_NAME"

# Define control file path for easier access
CONTROL_DIR="project/$PROJECT_NAME/control"

# 3. Initialize Intelligent Control Files
print_header "Step 2: Initializing Intelligent Control Files"

# --- backlog.yaml ---
cat > "$CONTROL_DIR/backlog.yaml" << EOF
# Product Backlog: List of high-level features and user stories.
# The autonomous system will pull from this list to plan sprints.
version: 1.0
stories:
  - id: USER-001
    title: "Implement User Authentication"
    description: "As a user, I want to be able to sign up and log in, so I can access my account."
    priority: "high"
    status: "todo"
EOF
print_success "Created backlog.yaml"

# --- sprint.yaml ---
cat > "$CONTROL_DIR/sprint.yaml" << EOF
# Sprint Plan: Defines the goal and scope for the current development cycle.
version: 1.0
sprint_id: "SPRINT-01"
goal: "Establish the core application shell and user authentication."
duration_days: 14
start_date: "$(date +'%Y-%m-%d')"
status: "not-started"
EOF
print_success "Created sprint.yaml"

# --- capabilities.yaml ---
cat > "$CONTROL_DIR/capabilities.yaml" << EOF
# Capabilities Registry: Lists the AI agents and their functions available to the system.
version: 1.0
agents:
   - "sparc-orchestrator"
   - "sparc-architect"
   - "sparc-specification-writer"
   - "sparc-pseudocode-designer"
   - "sparc-code-implementer"
   - "sparc-tdd-engineer"
   - "sparc-security-architect"
   - "security-reviewer"
   - "performance-engineer"
   - "integration-specialist"
   - "database-specialist"
   - "code-quality-specialist"
   - "technical-debt-manager"
   - "quality-assurance-coordinator"
   - "rapid-fact-checker"
EOF
print_success "Created capabilities.yaml"

# Initialize intelligent control plane
analyze_project_intelligence
configure_intelligent_circuit_breakers
initialize_quality_intelligence

# 4. Initialize Memory Bank Files
print_header "Step 3: Initializing Memory Bank"
# --- decisionLog.md ---
cat > "project/memory-bank/decisionLog.md" << EOF
# Enhanced Decision Log with Pattern Learning

*This log captures decisions with pattern recognition for autonomous learning and replication.*

---

## Decision Entry Template

### DECISION_[YYYY_MM_DD_HHmm]: [DECISION_TYPE]_[BRIEF_DESCRIPTION]

**Pattern Classification**: \`[authentication_decision|architecture_choice|security_implementation|performance_optimization]\`
**Decision Confidence**: [0.0-1.0]
**Complexity Score**: [0.0-1.0]
**Business Impact**: [Low|Medium|High|Critical]
EOF
print_success "Initialized enhanced decisionLog.md"
# --- delegationPatterns.md ---
cat > "project/memory-bank/delegationPatterns.md" << EOF
# Intelligent Delegation Patterns

*Successful delegation sequences with optimization metrics and auto-application logic.*

---

## Workflow Pattern Template

### PATTERN_[ID]: [PATTERN_NAME]
**Success Rate**: [X%] ([successful_implementations]/[total_attempts])
**Average Cycle Time**: [X.X] days
**Quality Score Average**: [0.XX]
**Optimization Level**: [Basic|Intermediate|Advanced]
EOF
print_success "Initialized intelligent delegationPatterns.md"

# --- learningHistory.md ---
cat > "memory-bank/learningHistory.md" << EOF
# Learning History

*A record of outcomes from various approaches. The system analyzes this history to refine its strategies, avoid repeating mistakes, and improve its predictive capabilities.*

---
EOF
print_success "Initialized learningHistory.md"

# --- productContext.md ---
cat > "memory-bank/productContext.md" << EOF
# Product Context

*This file contains the high-level business goals, target audience, and core value proposition for the project. It provides the 'why' behind the work.*

---
EOF
print_success "Initialized productContext.md"

# --- progress.md ---
cat > "memory-bank/progress.md" << EOF
# Progress Tracker

*A high-level summary of sprint-over-sprint progress, major milestones achieved, and overall project velocity.*

---
EOF
print_success "Initialized progress.md"
# --- systemPatterns.md ---
cat > "project/memory-bank/systemPatterns.md" << EOF
# System Patterns with Autonomous Learning

*Approved architectural patterns, technology stacks, and coding standards for this project.*

---

## Autonomous Pattern Recognition

### Pattern Learning Algorithm
\`\`\`yaml
pattern_detection:
  frequency_threshold: 3  # Pattern must occur 3+ times to be recognized
  success_rate_threshold: 0.75  # Must have 75%+ success rate
  confidence_building:
    initial_confidence: 0.5
    success_increment: 0.1
    failure_decrement: 0.15
    max_confidence: 0.95
\`\`\`
EOF
print_success "Initialized systemPatterns.md with autonomous learning"


# --- Finalization ---
print_header "🎉 Project Setup Complete! 🎉"
echo "Your new project '$PROJECT_NAME' is ready."
echo "Next steps:"
echo "1. Review the generated files in 'project/$PROJECT_NAME/control'."
echo "2. Update 'backlog.yaml' with your specific user stories."
echo "3. Initiate the autonomous workflow."
echo ""
