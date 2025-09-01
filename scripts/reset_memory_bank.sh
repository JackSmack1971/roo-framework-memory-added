#!/bin/bash

# ==============================================================================
# Roo Autonomous AI Development Framework - Memory Bank Reset Utility
# ==============================================================================
#
# Description:
#   This utility resets the Memory Bank for a fresh project run. It clears
#   the contents of dynamic log files (decisionLog, learningHistory, progress)
#   while preserving their headers.
#
#   IMPORTANT: It intentionally DOES NOT touch foundational knowledge files
#   (delegationPatterns, systemPatterns, productContext), as these contain
#   long-term learned behaviors and strategic context.
#
# Usage:
#   ./reset_memory_bank.sh
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

# --- Main Script ---

print_header "Roo Memory Bank Reset Utility"

# 1. Define File Paths and Headers
MEMORY_DIR="memory-bank"
# Files to be cleared (the logs of a specific run)
FILES_TO_RESET=(
  "decisionLog.md"
  "learningHistory.md"
  "progress.md"
)

# Files to be preserved (foundational knowledge)
FILES_TO_PRESERVE=(
  "delegationPatterns.md"
  "systemPatterns.md"
  "productContext.md"
)

# Define the default header content for each file
declare -A HEADERS
HEADERS["decisionLog.md"]="# Decision Log\n\n*This log records significant decisions made by the autonomous system, including architectural choices, conflict resolutions, and strategic pivots.*\n\n---"
HEADERS["learningHistory.md"]="# Learning History\n\n*A record of outcomes from various approaches. The system analyzes this history to refine its strategies, avoid repeating mistakes, and improve its predictive capabilities.*\n\n---"
HEADERS["progress.md"]="# Progress Tracker\n\n*A high-level summary of sprint-over-sprint progress, major milestones achieved, and overall project velocity.*\n\n---"

# 2. Check if the memory-bank directory exists
if [ ! -d "$MEMORY_DIR" ]; then
  echo "❌ Error: The '$MEMORY_DIR' directory was not found."
  echo "Please run this script from the project's root directory."
  exit 1
fi

# 3. Confirmation Prompt
echo "This script will reset the following files in '$MEMORY_DIR':"
for file in "${FILES_TO_RESET[@]}"; do
  echo "  - $file"
done
echo ""
echo "The following foundational files will NOT be changed:"
for file in "${FILES_TO_PRESERVE[@]}"; do
  echo "  - $file"
done
echo ""

read -p "Are you sure you want to proceed? (y/N) " -n 1 -r
echo # Move to a new line

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo "🚫 Reset cancelled by user."
  exit 0
fi

# 4. Reset the Files
print_header "Resetting Memory Bank Logs"

for file in "${FILES_TO_RESET[@]}"; do
  FILE_PATH="$MEMORY_DIR/$file"
  if [ -f "$FILE_PATH" ]; then
    # Use printf to correctly interpret the newlines in the header string
    printf "%b\n" "${HEADERS[$file]}" > "$FILE_PATH"
    print_success "Reset content of $file"
  else
    echo "⚠️  Warning: $file not found, skipping."
  fi
done

# --- Finalization ---
print_header "🎉 Memory Bank Reset Complete! 🎉"
echo "The decision, learning, and progress logs are now clean."
echo "The system is ready for a fresh run."
echo ""
