const fs = require('fs/promises');

class DocumentationGenerator {
  extractApiEndpoints(code) {
    const regex = /app\.(get|post|put|delete)\('([^']+)'/g;
    const endpoints = [];
    let match;
    while ((match = regex.exec(code))) {
      endpoints.push({ path: match[2], method: match[1].toUpperCase() });
    }
    return endpoints;
  }

  analyzeCodeFile(code, filename) {
    const functions = [];
    const functionRegex = /function\s+([a-zA-Z0-9_]+)/g;
    let match;
    while ((match = functionRegex.exec(code))) {
      functions.push({ name: match[1] });
    }
    const classes = [];
    const classRegex = /class\s+([a-zA-Z0-9_]+)/g;
    while ((match = classRegex.exec(code))) {
      classes.push({ name: match[1] });
    }
    return { functions, classes };
  }

  generateFunctionDocstring(name, params) {
    return `/**\n * ${name.replace(/([A-Z])/g, ' $1').trim()}\n * @param ${params}\n * @returns {any}\n */`;
  }

  async generateApiDocumentation(files) {
    return {
      openapi: '3.0.0',
      info: { title: 'API', version: '1.0.0' },
      paths: {}
    };
  }

  async writeFile(file, content) {
    await fs.writeFile(file, content);
    return true;
  }

  async readFile(file) {
    try {
      return await fs.readFile(file, 'utf8');
    } catch {
      return null;
    }
  }
}

module.exports = DocumentationGenerator;
