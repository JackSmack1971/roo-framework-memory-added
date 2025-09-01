# Deep Analysis: Roo Code .roomodes File Format and Functionality

## Overview of Roo Code

Roo Code is an AI-powered autonomous coding agent that lives in your editor. It's a VS Code extension that gives you a whole dev team of AI agents in your code editor. It can read and write files in your project, execute commands in your VS Code terminal, perform web browsing (if enabled), and use external tools via the Model Context Protocol (MCP).

## The .roomodes File: Purpose and Function

The `.roomodes` file is a **project-specific configuration file** that defines custom AI modes for Roo Code. These files define an array/list of custom modes that tailor Roo's behavior to specific tasks or workflows within a particular project.

### Key Functions:
- **Mode Specialization**: Create modes optimized for specific tasks like "Documentation Writer," "Test Engineer," or "Refactoring Expert"
- **Security & Access Control**: Restrict a mode's access to sensitive files or commands
- **Tool Group Management**: Control which tool groups (read, edit, browser, command, mcp) each mode can access
- **File-Type Restrictions**: Use regex patterns to limit which files a mode can edit
- **Custom Instructions**: Provide specialized behavioral guidelines for each mode

## File Format: YAML vs JSON Support

Roo Code now supports both YAML (preferred) and JSON formats. Both .roomodes files and global configuration files can be either YAML or JSON format.

### Format Detection and Migration
Roo Code automatically detects the format of .roomodes files by attempting to parse them as YAML first. The system follows this priority:

1. **YAML Preferred**: New modes created via UI default to YAML
2. **Automatic Detection**: Parser attempts YAML first, falls back to JSON
3. **UI Conversion**: If you edit a project-specific mode through the Roo Code UI and the existing .roomodes file is in JSON format, Roo Code will save the changes in YAML format

## Core Structure and Properties

### Root Structure
```yaml
customModes:
  - slug: mode-identifier
    name: Display Name
    description: Short UI description
    roleDefinition: Detailed behavior definition
    whenToUse: Orchestration guidance
    customInstructions: Additional guidelines
    groups: [tool-group-array]
    source: project  # Auto-added by system
```

### Property Specifications

#### 1. `slug` (Required)
- **Purpose**: Unique internal identifier for the mode
- **Format**: Must match the pattern /^[a-zA-Z0-9-]+$/ (only letters, numbers, and hyphens)
- **Usage**: Used in file/directory names for mode-specific rules (`.roo/rules-{slug}/`)
- **Validation**: System enforces uniqueness and format compliance

#### 2. `name` (Required)
- **Purpose**: Display name shown in Roo Code UI
- **Format**: Human-readable, can include spaces, emojis, and special characters
- **Example**: `"ðŸ“ Documentation Writer"`, `"ðŸ§ª Test Engineer"`

#### 3. `description` (Optional but Recommended)
- **Purpose**: A short, user-friendly summary displayed below the mode name in the mode selector UI
- **UI Display**: Appears in the redesigned mode selector
- **Best Practice**: Keep concise and focused on what the mode does for the user

#### 4. `roleDefinition` (Required)
- **Purpose**: Detailed description of the mode's role, expertise, and personality
- **Placement**: This text is placed at the beginning of the system prompt when the mode is active
- **Supports Multi-line**: Both YAML block scalars (`|-` or `>-`) and JSON strings

#### 5. `whenToUse` (Optional)
- **Purpose**: Provides guidance for Roo's automated decision-making, particularly for mode selection and task orchestration
- **Usage**: This field is used by Roo for automated decisions and is not displayed in the mode selector UI
- **Orchestration**: Used by the Orchestrator mode for task delegation

#### 6. `groups` (Required)
- **Purpose**: Defines which tool groups the mode can access
- **Available Groups**: `"read"`, `"edit"`, `"browser"`, `"command"`, `"mcp"`
- **Structure**: Can be simple strings or tuples for restrictions

#### 7. `customInstructions` (Optional)
- **Purpose**: A string containing additional behavioral guidelines for the mode
- **Placement**: This text is added near the end of the system prompt
- **Supplementation**: Can be enhanced with file-based instructions

## Advanced File Restrictions

### Edit Group Restrictions
The `groups` property supports sophisticated file restrictions using regex patterns:

#### YAML Syntax:
```yaml
groups:
  - read
  - - edit  # First element of tuple
    - fileRegex: \.(js|ts)$  # Second element is options object
      description: JS/TS files only
  - command
```

#### JSON Syntax:
```json
"groups": [
  "read",
  ["edit", { 
    "fileRegex": "\\.(js|ts)$", 
    "description": "JS/TS files only" 
  }],
  "command"
]
```

### Regex Pattern Rules
Patterns match against the full relative file path from your workspace root (e.g., src/components/button.js)

**Escaping Differences**:
- **YAML**: In unquoted or single-quoted YAML strings, a single backslash is usually sufficient for regex special characters (e.g., \.md$)
- **JSON**: In JSON strings, backslashes (\) must be double-escaped (e.g., \\.md$)

## Key Differences from Conventional YAML/JSON

### 1. Schema Validation
Unlike generic YAML/JSON, `.roomodes` files have strict schema validation:
- **Required Properties**: `slug`, `name`, `roleDefinition`, `groups`
- **Format Constraints**: Slug must match specific regex pattern
- **Tool Group Validation**: Only predefined tool groups are allowed
- **Regex Validation**: File restriction patterns are validated

### 2. Special Tuple Syntax for Tool Groups
The `groups` array uses a unique tuple syntax for restrictions that differs from standard YAML/JSON arrays:
```yaml
# Standard array syntax
groups: ["read", "edit", "command"]

# Special tuple syntax for restrictions
groups:
  - read
  - - edit
    - fileRegex: pattern
      description: optional
```

### 3. Automatic Property Injection
The source property is automatically added by the system and shouldn't be manually set. The system injects:
- `source: "project"` for project-specific modes
- `source: "global"` for global modes

### 4. Path Normalization
When exporting modes with rules, all file paths are normalized to use forward slashes for cross-platform compatibility.

### 5. Multi-line String Handling
YAML advantages for `.roomodes`:
```yaml
# YAML literal block (preserves line breaks)
roleDefinition: |-
  You are a test engineer with expertise in:
  - Writing comprehensive test suites
  - Test-driven development
  - Integration testing

# YAML folded block (converts to single line)
roleDefinition: >-
  You are a test engineer with expertise in writing comprehensive
  test suites and test-driven development.
```

## File Location and Precedence

### Project vs Global Modes
- **Project**: `.roomodes` in project root
- **Global**: `custom_modes.yaml` or `custom_modes.json` in user settings

### Configuration Precedence
Mode configurations are applied in this order: 1. Project-level mode configurations (from .roomodes - YAML or JSON), 2. Global mode configurations, 3. Default mode configurations

**Important**: When modes with the same slug exist in both .roomodes and global settings, the .roomodes version completely overrides the global one. This applies to ALL properties, not just some.

## Mode-Specific Instructions

### Directory-Based Instructions (Preferred)
```
.roo/rules-{mode-slug}/
â”œâ”€â”€ 01-style-guide.md
â”œâ”€â”€ 02-formatting.txt
â””â”€â”€ subdirectory/
    â””â”€â”€ more-rules.md
```

### File-Based Instructions (Fallback)
```
.roorules-{mode-slug}
```

The directory-based method (.roo/rules-{mode-slug}/) takes precedence. If this directory exists and contains files, any corresponding root-level .roorules-{mode-slug} file will be ignored for that mode.

## What's NOT Allowed

### 1. Invalid Slug Formats
```yaml
# âŒ INVALID - contains spaces and special chars
slug: "my mode!"

# âŒ INVALID - starts with number
slug: "2-mode"

# âœ… VALID
slug: "my-mode-2"
```

### 2. Invalid Tool Groups
```yaml
# âŒ INVALID - non-existent tool group
groups: ["read", "write", "execute"]

# âœ… VALID - only predefined groups
groups: ["read", "edit", "command"]
```

### 3. Malformed Regex Patterns
```yaml
# âŒ INVALID - unclosed bracket
groups:
  - - edit
    - fileRegex: \.(js|ts$

# âœ… VALID
groups:
  - - edit
    - fileRegex: \.(js|ts)$
```

### 4. Manual Source Property
```yaml
# âŒ INVALID - system manages this
source: "manual"

# âœ… VALID - omit entirely
# source property is auto-injected
```

## Error Handling and Validation

### Common Error Types
1. **Schema Validation Errors**: Missing required properties or invalid types
2. **Regex Compilation Errors**: Invalid file restriction patterns
3. **Slug Conflicts**: Duplicate slugs within the same scope
4. **Tool Group Errors**: References to non-existent tool groups

### FileRestrictionError
When a mode attempts to edit a restricted file:
- Mode name and description
- Allowed file pattern
- Attempted file path
- Blocked tool information

## Import/Export Functionality

### Export Format
```yaml
customModes:
  - slug: "my-custom-mode"
    name: "My Custom Mode"
    roleDefinition: "You are a helpful assistant."
    groups: ["read", "edit"]
rulesFiles:
  - relativePath: "rules-my-custom-mode/rules.md"
    content: "These are the rules for my custom mode."
```

### Slug Change Support
When you change the slug in an exported YAML file before importing, the import process updates the rule file paths to match the new slug.

## Best Practices

### 1. Use YAML Format
- Better readability and maintainability
- Support for comments and multi-line strings
- Preferred by the Roo Code team

### 2. Validate Regex Patterns
- Test patterns with sample file paths
- Use online regex testers
- Remember escaping rules for your format

### 3. Keep Slugs Descriptive
- Use kebab-case (hyphens)
- Make them meaningful: `docs-writer` not `dw`

### 4. Leverage File Restrictions
- Enhance security by limiting edit access
- Prevent accidental modifications to critical files
- Use descriptive restriction messages

### 5. Organize Complex Instructions
- Use directory-based rules for complex modes
- Break instructions into logical files
- Use meaningful file names with prefixes for ordering

## Troubleshooting Common Issues

### Mode Not Appearing
- Reload VS Code window after creating/importing modes
- Check for YAML/JSON syntax errors
- Verify slug uniqueness

### Regex Validation Failures
- Test patterns in isolation
- Check escaping rules for your format
- Validate against actual file paths in your project

### Precedence Confusion
- Remember project modes completely override global modes
- Check configuration precedence order
- Use distinct slugs to avoid conflicts