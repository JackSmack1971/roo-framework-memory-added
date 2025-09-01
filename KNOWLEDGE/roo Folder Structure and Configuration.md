# Deep Analysis: Roo Code .roo Folder Structure and Configuration

## Overview

Roo Code is a VS Code extension that provides AI-powered autonomous coding capabilities. The `.roo` folder serves as the configuration hub for customizing AI behavior through custom instructions, rules, and system prompt overrides.

## Core Function of the .roo Folder

The .roo folder system allows developers to customize how Roo behaves by providing specific guidance that shapes responses, coding style, and decision-making processes at both global and project levels.

### Location Hierarchy

**Global Configuration:**
- Linux/macOS: `~/.roo/`
- Windows: `%USERPROFILE%\.roo\`

**Workspace Configuration:**
- Project root: `./roo/`

## Directory Structure and Configuration Options

### 1. Rules Directories

#### General Rules (All Modes)
```
.roo/
â”œâ”€â”€ rules/                    # Workspace-wide rules for all modes
â”‚   â”œâ”€â”€ 01-coding-standards.md
â”‚   â”œâ”€â”€ 02-formatting-rules.md
â”‚   â””â”€â”€ 03-security-guidelines.md
```

#### Mode-Specific Rules
```
.roo/
â”œâ”€â”€ rules-code/              # Rules specific to Code mode
â”‚   â”œâ”€â”€ typescript-rules.md
â”‚   â””â”€â”€ testing-requirements.md
â”œâ”€â”€ rules-debug/             # Rules for Debug mode
â”œâ”€â”€ rules-architect/         # Rules for Architect mode
â”œâ”€â”€ rules-ask/              # Rules for Ask mode
â””â”€â”€ rules-{custom-mode}/    # Rules for custom modes
```

### 2. System Prompt Overrides (Footgun Feature)

Advanced users can create custom system prompts for specific modes by placing a `.roo/system-prompt-{mode-slug}` file in their workspace. When present, Roo uses this file instead of generating the standard system prompt sections, allowing for complete customization of Roo's behavior in that mode.

```
.roo/
â”œâ”€â”€ system-prompt-code       # Custom system prompt for Code mode
â”œâ”€â”€ system-prompt-debug      # Custom system prompt for Debug mode
â”œâ”€â”€ system-prompt-architect  # Custom system prompt for Architect mode
â””â”€â”€ system-prompt-{mode}     # Custom system prompts for other modes
```

#### Template Variables in System Prompts
Roo Code supports template variables in custom system prompts:
- `{{workspace}}`: File path to project workspace root
- `{{mode}}`: Current mode name
- `{{operatingSystem}}`: User's operating system
- `{{shell}}`: Default shell
- `{{language}}`: Response language preference

### 3. Mode Configuration Files

Custom modes can be defined using YAML or JSON format in `.roomodes` files, with YAML being the default for new modes created via the UI.

```
.roo/
â”œâ”€â”€ custom_modes.yaml        # Custom mode definitions
â””â”€â”€ custom_modes.json        # Alternative JSON format
```

## Configuration File Types and Formats

### Supported File Formats

#### Rules Files
- **Markdown** (`.md`) - Recommended
- **Text** (`.txt`) - Basic text format
- **Any text-based format** - Content is read as-is

#### Configuration Files
- **YAML** (`.yaml`, `.yml`) - Preferred format
- **JSON** (`.json`) - Fully supported legacy format

### File Loading Behavior

Rules are loaded recursively from directories, with content appended to the system prompt in alphabetical order based on filename. Empty or missing rule files are silently skipped.

## Rule Loading Priority and Hierarchy

Instructions are combined in this exact order:

1. **Language Preference** (if set)
2. **Global Instructions** (from Prompts Tab)
3. **Mode-specific Instructions** (from Prompts Tab)
4. **Global Rules** (from `~/.roo/`)
   - Mode-specific: `~/.roo/rules-{modeSlug}/`
   - General: `~/.roo/rules/`
5. **Workspace Rules** (from `.roo/`)
   - Mode-specific: `.roo/rules-{modeSlug}/`
   - General: `.roo/rules/`

### Directory vs File Precedence

**Directory Method (Preferred):**
- `.roo/rules/` - Workspace-wide rules
- `.roo/rules-{modeSlug}/` - Mode-specific rules

**Fallback Method:**
- `.roorules` - Single workspace-wide rules file
- `.roorules-{modeSlug}` - Single mode-specific rules file

Directory-based rules take precedence over file-based fallbacks when both exist.

## Advanced Configuration Options

### 1. Custom Mode Properties

Custom modes can be configured with several key properties including slug, role definition, tool access, file permissions, and specialized instructions.

```yaml
customModes:
  - slug: my-custom-mode
    name: "My Custom Mode"
    roleDefinition: "You are a specialized assistant for..."
    customInstructions: "Additional specific instructions..."
    fileRegex: "\\.(js|ts)$"  # File access patterns
```

### 2. Tool Access Control

Custom modes can restrict or allow specific tools based on the task requirements.

### 3. File Permission Patterns

Modes can define `fileRegex` patterns to control which files the AI can access, providing security and focus boundaries.

### 4. Shared Rules Directory

There's a generic `.roo/rules/` directory (without mode suffix) that can be used for shared rules across all modes.

## Global vs. Workspace Configuration Strategy

### Global Configuration Benefits
Global rules provide consistency across all projects and eliminate the need to maintain separate rule files in each project.

- Organization-wide coding standards
- Consistent development workflows
- Easy maintenance and updates

### Workspace Configuration Benefits
- Project-specific requirements
- Team collaboration standards
- Version control integration

### Hybrid Approach
Combine global rules for organization standards with project-specific workspace rules for project-specific requirements. Workspace rules can override global rules when needed.

## Best Practices

### 1. File Organization
- Use numbered prefixes (01-, 02-) to control loading order
- Group related rules in logical files
- Use descriptive filenames

### 2. Rule Writing
- Be specific and actionable
- Provide examples when possible
- Consider the impact on all modes vs. specific modes

### 3. Version Control
- Include `.roo/rules/` directories in version control
- Document team-specific configuration requirements
- Maintain consistency across team members

### 4. Testing and Validation
Test regex patterns using online regex testers before applying them, and reload VS Code window after creating or importing modes.

## Integration with Cursor Rules

Roo Code can leverage community-made Cursor rules (.mdc files) by placing them in the appropriate `.roo/rules-{mode}/` directories, allowing access to a vast collection of specialized development rules.

## Error Handling and Troubleshooting

### Common Issues
- **Mode not appearing**: Reload VS Code window after creating modes
- **Invalid regex patterns**: Test patterns before applying
- **YAML syntax errors**: Validate YAML format and indentation
- **Rule precedence**: Understand the loading order hierarchy

### Safety Considerations
System prompt overrides should be used cautiously as incorrect implementation can significantly degrade Roo Code's performance and reliability. This feature is intended for users deeply familiar with Roo Code's prompting system.

## Conclusion

The `.roo` folder system provides powerful customization capabilities for Roo Code, enabling developers to create specialized AI assistants tailored to specific workflows, coding standards, and project requirements. The hierarchical configuration system supports both global consistency and project-specific customization, making it suitable for individual developers and teams alike.