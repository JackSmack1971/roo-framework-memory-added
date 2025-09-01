#!/usr/bin/env node

/**
 * Documentation Generation Script
 *
 * CLI tool for generating documentation from code
 * Used by TDD Engineer and Code Implementer modes
 */

const fs = require('fs/promises');
const path = require('path');
const { glob } = require('glob');
const DocumentationGenerator = require('../memory-bank/lib/documentation-generator.js');

class DocumentationCLI {
  constructor() {
    this.generator = new DocumentationGenerator();
  }

  async run() {
    const command = process.argv[2];

    switch (command) {
      case 'api':
        await this.generateApiDocs();
        break;
      case 'code':
        await this.generateCodeDocs();
        break;
      case 'readme':
        await this.generateReadme();
        break;
      case 'architecture':
        await this.generateArchitectureDocs();
        break;
      case 'all':
        await this.generateAllDocs();
        break;
      default:
        this.showHelp();
    }
  }

  async generateApiDocs() {
    console.log('🔍 Analyzing code for API endpoints...');

    const sourceFiles = await this.findSourceFiles();
    const apiDocs = await this.generator.generateApiDocumentation(sourceFiles, {
      title: 'API Documentation',
      version: '1.0.0',
      description: 'Auto-generated API documentation'
    });

    // Write OpenAPI spec
    const openApiPath = 'docs/api/openapi.yaml';
    await this.writeYamlFile(openApiPath, apiDocs);

    // Write API documentation
    const apiDocPath = 'docs/api/endpoints.md';
    const apiMarkdown = this.convertOpenApiToMarkdown(apiDocs);
    await this.writeFile(apiDocPath, apiMarkdown);

    console.log(`✅ API documentation generated:`);
    console.log(`   - ${openApiPath}`);
    console.log(`   - ${apiDocPath}`);
  }

  async generateCodeDocs() {
    console.log('📝 Analyzing code for documentation...');

    const sourceFiles = await this.findSourceFiles();
    const codeDocs = await this.generator.generateCodeDocumentation(sourceFiles);

    // Write module documentation
    for (const module of codeDocs.modules) {
      const docPath = `docs/code/${module.file.replace(/\.[^/.]+$/, '')}.md`;
      const docContent = this.generateModuleMarkdown(module);
      await this.writeFile(docPath, docContent);
    }

    // Update source files with docstrings
    await this.updateSourceFilesWithDocstrings(codeDocs);

    console.log(`✅ Code documentation generated for ${codeDocs.modules.length} modules`);
  }

  async generateReadme() {
    console.log('📖 Generating README documentation...');

    const projectInfo = await this.analyzeProject();
    const readme = await this.generator.generateReadmeDocumentation(projectInfo);

    const readmePath = 'README.md';
    const readmeContent = this.convertReadmeToMarkdown(readme);

    // Check if README exists and merge if needed
    const existingReadme = await this.readFile(readmePath);
    if (existingReadme) {
      const mergedContent = this.mergeReadmeContent(existingReadme, readmeContent);
      await this.writeFile(readmePath, mergedContent);
      console.log('✅ README.md updated with generated content');
    } else {
      await this.writeFile(readmePath, readmeContent);
      console.log('✅ README.md generated');
    }
  }

  async generateArchitectureDocs() {
    console.log('🏗️ Analyzing system for architecture documentation...');

    const components = await this.analyzeComponents();
    const architecture = await this.generator.generateArchitectureDocumentation(components);

    // Write architecture overview
    const overviewPath = 'docs/architecture/overview.md';
    await this.writeFile(overviewPath, architecture.overview);

    // Write component documentation
    const componentsPath = 'docs/architecture/components.md';
    const componentsContent = this.generateComponentsMarkdown(architecture.components);
    await this.writeFile(componentsPath, componentsContent);

    // Write diagrams
    const componentDiagramPath = 'docs/architecture/diagrams/components.puml';
    await this.writeFile(componentDiagramPath, architecture.diagrams.component);

    const dataFlowDiagramPath = 'docs/architecture/diagrams/data-flow.puml';
    await this.writeFile(dataFlowDiagramPath, architecture.diagrams.dataFlow);

    console.log('✅ Architecture documentation generated');
  }

  async generateAllDocs() {
    console.log('🚀 Generating all documentation...');

    await this.generateApiDocs();
    await this.generateCodeDocs();
    await this.generateArchitectureDocs();
    await this.generateReadme();

    console.log('✅ All documentation generated successfully!');
  }

  async findSourceFiles() {
    const patterns = [
      'src/**/*.{js,ts,py}',
      'lib/**/*.{js,ts,py}',
      '**/*.{js,ts,py}',
      '!node_modules/**',
      '!dist/**',
      '!build/**',
      '!__pycache__/**',
      '!*.test.{js,ts,py}',
      '!*.spec.{js,ts,py}'
    ];

    const files = [];
    for (const pattern of patterns) {
      try {
        const matches = await glob(pattern, { cwd: process.cwd() });
        files.push(...matches);
      } catch (error) {
        // Ignore glob errors for patterns that don't match
      }
    }

    return [...new Set(files)]; // Remove duplicates
  }

  async analyzeProject() {
    const projectInfo = {
      name: 'Project',
      description: 'Auto-generated project description',
      features: [],
      apiEndpoints: [],
      packageManager: 'npm',
      language: 'javascript'
    };

    // Read package.json for project info
    try {
      const packageJson = await this.readJsonFile('package.json');
      if (packageJson) {
        projectInfo.name = packageJson.name || projectInfo.name;
        projectInfo.description = packageJson.description || projectInfo.description;
        projectInfo.packageManager = 'npm';
        projectInfo.language = 'javascript';
      }
    } catch (error) {
      // Try Python project
      try {
        const pyprojectToml = await this.readFile('pyproject.toml');
        if (pyprojectToml) {
          projectInfo.packageManager = 'pip';
          projectInfo.language = 'python';
        }
      } catch (error) {
        // Keep defaults
      }
    }

    // Analyze source files for features
    const sourceFiles = await this.findSourceFiles();
    projectInfo.features = await this.extractFeatures(sourceFiles);

    // Extract API endpoints
    for (const file of sourceFiles.slice(0, 5)) { // Limit for performance
      try {
        const content = await this.readFile(file);
        const endpoints = this.generator.extractApiEndpoints(content);
        projectInfo.apiEndpoints.push(...endpoints);
      } catch (error) {
        // Ignore file read errors
      }
    }

    return projectInfo;
  }

  async analyzeComponents() {
    const components = [];

    // Analyze source files for components
    const sourceFiles = await this.findSourceFiles();

    for (const file of sourceFiles) {
      try {
        const content = await this.readFile(file);
        const fileComponents = this.extractComponentsFromFile(content, file);
        components.push(...fileComponents);
      } catch (error) {
        // Ignore file read errors
      }
    }

    // Remove duplicates and merge similar components
    return this.mergeComponents(components);
  }

  extractComponentsFromFile(content, filePath) {
    const components = [];
    const fileName = path.basename(filePath, path.extname(filePath));

    // Simple component extraction based on file structure and content
    if (content.includes('class ') || content.includes('function ') || content.includes('def ')) {
      const type = this.inferComponentType(filePath, content);

      components.push({
        name: fileName,
        type: type,
        description: `Auto-detected ${type} component`,
        dependencies: this.extractDependencies(content),
        interfaces: this.extractInterfaces(content),
        technologies: this.inferTechnologies(filePath, content),
        file: filePath
      });
    }

    return components;
  }

  inferComponentType(filePath, content) {
    const fileName = path.basename(filePath).toLowerCase();

    if (fileName.includes('api') || fileName.includes('route') || fileName.includes('endpoint')) {
      return 'api';
    } else if (fileName.includes('service') || fileName.includes('business')) {
      return 'service';
    } else if (fileName.includes('model') || fileName.includes('entity') || fileName.includes('schema')) {
      return 'model';
    } else if (fileName.includes('controller') || fileName.includes('handler')) {
      return 'controller';
    } else if (fileName.includes('util') || fileName.includes('helper')) {
      return 'utility';
    } else if (content.includes('database') || content.includes('db') || content.includes('sql')) {
      return 'database';
    } else if (content.includes('react') || content.includes('component') || content.includes('jsx')) {
      return 'frontend';
    } else {
      return 'module';
    }
  }

  extractDependencies(content) {
    const dependencies = [];

    // Extract imports/requires
    const importPatterns = [
      /import\s+.*\s+from\s+['"]([^'"]+)['"]/g,
      /require\s*\(\s*['"]([^'"]+)['"]\s*\)/g,
      /from\s+([^\s]+)/g
    ];

    for (const pattern of importPatterns) {
      let match;
      while ((match = pattern.exec(content)) !== null) {
        const dependency = match[1];
        if (dependency && !dependency.startsWith('.') && !dependency.startsWith('/')) {
          dependencies.push(dependency);
        }
      }
    }

    return [...new Set(dependencies)].slice(0, 5); // Limit dependencies
  }

  extractInterfaces(content) {
    const interfaces = [];

    // Extract function signatures
    const functionPattern = /(?:function|def|const|let|var)\s+(\w+)\s*\(([^)]*)\)/g;
    let match;
    while ((match = functionPattern.exec(content)) !== null) {
      interfaces.push({
        name: match[1],
        parameters: match[2],
        type: 'function'
      });
    }

    return interfaces.slice(0, 10); // Limit interfaces
  }

  inferTechnologies(filePath, content) {
    const technologies = [];
    const fileExt = path.extname(filePath).toLowerCase();

    // Infer from file extension
    if (fileExt === '.js') {
      technologies.push('JavaScript');
      if (content.includes('express')) technologies.push('Express.js');
      if (content.includes('react')) technologies.push('React');
      if (content.includes('mongoose')) technologies.push('MongoDB');
    } else if (fileExt === '.ts') {
      technologies.push('TypeScript');
      if (content.includes('express')) technologies.push('Express.js');
      if (content.includes('react')) technologies.push('React');
    } else if (fileExt === '.py') {
      technologies.push('Python');
      if (content.includes('flask')) technologies.push('Flask');
      if (content.includes('django')) technologies.push('Django');
      if (content.includes('sqlalchemy')) technologies.push('SQLAlchemy');
    }

    return technologies;
  }

  mergeComponents(components) {
    const merged = new Map();

    for (const component of components) {
      const key = component.name.toLowerCase();
      if (merged.has(key)) {
        const existing = merged.get(key);
        // Merge dependencies and interfaces
        existing.dependencies = [...new Set([...existing.dependencies, ...component.dependencies])];
        existing.interfaces = [...new Set([...existing.interfaces, ...component.interfaces])];
        existing.technologies = [...new Set([...existing.technologies, ...component.technologies])];
      } else {
        merged.set(key, { ...component });
      }
    }

    return Array.from(merged.values());
  }

  async extractFeatures(sourceFiles) {
    const features = new Set();

    for (const file of sourceFiles.slice(0, 10)) { // Limit for performance
      try {
        const content = await this.readFile(file);
        const fileFeatures = this.extractFeaturesFromContent(content);
        fileFeatures.forEach(f => features.add(f));
      } catch (error) {
        // Ignore file read errors
      }
    }

    return Array.from(features).slice(0, 10); // Limit features
  }

  extractFeaturesFromContent(content) {
    const features = [];

    // Simple feature extraction based on function names and comments
    const lines = content.split('\n');
    for (const line of lines) {
      const trimmed = line.trim();
      if (trimmed.startsWith('//') || trimmed.startsWith('#') || trimmed.startsWith('*')) {
        const comment = trimmed.replace(/^\/\/|^#|^\*\s*/, '');
        if (comment.length > 10 && comment.length < 100) {
          features.push(comment);
        }
      }
    }

    return features;
  }

  // Utility methods for file operations
  async readFile(filePath) {
    try {
      return await fs.readFile(filePath, 'utf8');
    } catch {
      return null;
    }
  }

  async readJsonFile(filePath) {
    try {
      const content = await this.readFile(filePath);
      return content ? JSON.parse(content) : null;
    } catch {
      return null;
    }
  }

  async writeFile(filePath, content) {
    try {
      await fs.mkdir(path.dirname(filePath), { recursive: true });
      await fs.writeFile(filePath, content, 'utf8');
      return true;
    } catch (error) {
      console.error(`Failed to write ${filePath}: ${error.message}`);
      return false;
    }
  }

  async writeYamlFile(filePath, data) {
    try {
      const yaml = require('js-yaml');
      const content = yaml.dump(data);
      return await this.writeFile(filePath, content);
    } catch (error) {
      console.error(`Failed to write YAML ${filePath}: ${error.message}`);
      return false;
    }
  }

  // Markdown generation methods
  convertOpenApiToMarkdown(openapi) {
    let markdown = '# API Endpoints\n\n';

    if (openapi.paths) {
      for (const [path, methods] of Object.entries(openapi.paths)) {
        for (const [method, details] of Object.entries(methods)) {
          markdown += `## ${method.toUpperCase()} ${path}\n\n`;
          markdown += `${details.summary || 'API endpoint'}\n\n`;

          if (details.parameters && details.parameters.length > 0) {
            markdown += '**Parameters:**\n';
            for (const param of details.parameters) {
              markdown += `- \`${param.name}\` (${param.schema?.type || 'string'}): ${param.description || 'Parameter description'}\n`;
            }
            markdown += '\n';
          }

          if (details.responses) {
            markdown += '**Responses:**\n';
            for (const [code, response] of Object.entries(details.responses)) {
              markdown += `- \`${code}\`: ${response.description || 'Response description'}\n`;
            }
            markdown += '\n';
          }
        }
      }
    }

    return markdown;
  }

  generateModuleMarkdown(module) {
    let markdown = `# ${module.file}\n\n`;
    markdown += `**Complexity:** ${module.complexity.toFixed(1)}\n\n`;

    if (module.functions.length > 0) {
      markdown += '## Functions\n\n';
      for (const func of module.functions) {
        markdown += `### ${func.name}\n\n`;
        markdown += `- **Parameters:** ${func.parameters.map(p => `${p.name}: ${p.type}`).join(', ') || 'None'}\n`;
        markdown += `- **Complexity:** ${func.complexity}\n`;
        markdown += `- **File:** ${func.file}\n\n`;
      }
    }

    if (module.classes.length > 0) {
      markdown += '## Classes\n\n';
      for (const cls of module.classes) {
        markdown += `### ${cls.name}\n\n`;
        markdown += `- **Methods:** ${cls.methods.length}\n`;
        markdown += `- **File:** ${cls.file}\n\n`;
      }
    }

    return markdown;
  }

  convertReadmeToMarkdown(readme) {
    let markdown = readme.sections.map(section => {
      return `## ${section.title}\n\n${section.content}\n\n`;
    }).join('');

    return readme.title + '\n\n' + readme.description + '\n\n' + markdown;
  }

  generateComponentsMarkdown(components) {
    let markdown = '# System Components\n\n';

    for (const component of components) {
      markdown += `## ${component.name}\n\n`;
      markdown += `**Type:** ${component.type}\n\n`;
      markdown += `**Description:** ${component.description}\n\n`;

      if (component.technologies && component.technologies.length > 0) {
        markdown += `**Technologies:** ${component.technologies.join(', ')}\n\n`;
      }

      if (component.dependencies && component.dependencies.length > 0) {
        markdown += `**Dependencies:**\n`;
        for (const dep of component.dependencies) {
          markdown += `- ${dep}\n`;
        }
        markdown += '\n';
      }

      if (component.interfaces && component.interfaces.length > 0) {
        markdown += `**Interfaces:** ${component.interfaces.length} functions\n\n`;
      }

      markdown += `**File:** ${component.file}\n\n`;
    }

    return markdown;
  }

  mergeReadmeContent(existing, generated) {
    // Simple merge strategy - keep existing content and append generated sections
    return existing + '\n\n---\n\n## Auto-Generated Documentation\n\n' + generated;
  }

  async updateSourceFilesWithDocstrings(codeDocs) {
    for (const module of codeDocs.modules) {
      try {
        const filePath = module.file;
        let content = await this.readFile(filePath);

        if (!content) continue;

        // Add module docstring at the top if not present
        if (!content.includes('/**') && module.documentation) {
          content = module.documentation + '\n' + content;
        }

        // Add function docstrings
        for (const func of module.functions) {
          if (func.docstring && !this.hasDocstring(content, func.name)) {
            content = this.addDocstringToFunction(content, func.name, func.docstring);
          }
        }

        await this.writeFile(filePath, content);
      } catch (error) {
        console.warn(`Failed to update ${module.file}: ${error.message}`);
      }
    }
  }

  hasDocstring(content, functionName) {
    const lines = content.split('\n');
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      if (line.includes(functionName) && i > 0) {
        // Check if there's a docstring comment above the function
        for (let j = i - 1; j >= Math.max(0, i - 10); j--) {
          if (lines[j].includes('/**') || lines[j].includes('///')) {
            return true;
          }
          if (lines[j].trim() !== '' && !lines[j].includes('//') && !lines[j].includes('#')) {
            break;
          }
        }
      }
    }
    return false;
  }

  addDocstringToFunction(content, functionName, docstring) {
    const lines = content.split('\n');
    for (let i = 0; i < lines.length; i++) {
      if (lines[i].includes(functionName) && lines[i].includes('function') || lines[i].includes('def ') || lines[i].includes('const ') || lines[i].includes('let ')) {
        // Insert docstring before the function
        const docstringLines = docstring.split('\n');
        lines.splice(i, 0, ...docstringLines, '');
        break;
      }
    }
    return lines.join('\n');
  }

  showHelp() {
    console.log(`
Documentation Generator CLI

Usage: node generate-documentation.js <command>

Commands:
  api          Generate API documentation from code
  code         Generate code documentation and docstrings
  readme       Generate or update README.md
  architecture Generate architecture documentation
  all          Generate all documentation types

Examples:
  node generate-documentation.js api
  node generate-documentation.js all

This tool analyzes your codebase and generates comprehensive documentation automatically.
`);
  }
}

// Run the CLI if this script is executed directly
if (require.main === module) {
  const cli = new DocumentationCLI();
  cli.run().catch(error => {
    console.error('Documentation generation failed:', error.message);
    process.exit(1);
  });
}

module.exports = DocumentationCLI;