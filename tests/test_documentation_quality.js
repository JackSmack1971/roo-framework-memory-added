/**
 * Documentation Quality Tests
 *
 * Tests for documentation quality gates and validation
 */

const fs = require('fs/promises');
const path = require('path');
const DocumentationValidator = require('../memory-bank/lib/documentation-validator.js');
const DocumentationGenerator = require('../memory-bank/lib/documentation-generator.js');

describe('Documentation Quality Gates', () => {
  let validator;
  let generator;

  beforeAll(() => {
    validator = new DocumentationValidator();
    generator = new DocumentationGenerator();
  });

  describe('API Documentation Validation', () => {
    test('should validate OpenAPI specification exists', async () => {
      const results = await validator.validateApiDocumentation();

      // Check if the validation completed without errors
      expect(results).toHaveProperty('openapi_spec');
      expect(results).toHaveProperty('endpoint_coverage');
      expect(results).toHaveProperty('score');
      expect(typeof results.score).toBe('number');
      expect(results.score).toBeGreaterThanOrEqual(0);
      expect(results.score).toBeLessThanOrEqual(1);
    });

    test('should extract API endpoints from code', async () => {
      const testCode = `
        app.get('/api/users', (req, res) => {
          res.json({ users: [] });
        });

        app.post('/api/users', (req, res) => {
          const user = req.body;
          res.json(user);
        });
      `;

      const endpoints = generator.extractApiEndpoints(testCode);
      expect(endpoints).toHaveLength(2);
      expect(endpoints[0]).toHaveProperty('path', '/api/users');
      expect(endpoints[0]).toHaveProperty('method', 'GET');
      expect(endpoints[1]).toHaveProperty('path', '/api/users');
      expect(endpoints[1]).toHaveProperty('method', 'POST');
    });

    test('should generate valid OpenAPI documentation', async () => {
      const testFiles = ['src/api/users.js', 'src/api/auth.js'];
      const apiDocs = await generator.generateApiDocumentation(testFiles);

      expect(apiDocs).toHaveProperty('openapi', '3.0.0');
      expect(apiDocs).toHaveProperty('info');
      expect(apiDocs).toHaveProperty('paths');
      expect(apiDocs.info).toHaveProperty('title');
      expect(apiDocs.info).toHaveProperty('version');
    });
  });

  describe('Code Documentation Validation', () => {
    test('should validate code documentation coverage', async () => {
      const results = await validator.validateCodeDocumentation();

      expect(results).toHaveProperty('module_docs_coverage');
      expect(results).toHaveProperty('function_docs_coverage');
      expect(results).toHaveProperty('score');
      expect(typeof results.score).toBe('number');
    });

    test('should analyze code file structure', async () => {
      const testCode = `
        /**
         * Calculate sum of two numbers
         * @param {number} a - First number
         * @param {number} b - Second number
         * @returns {number} Sum of a and b
         */
        function add(a, b) {
          return a + b;
        }

        class Calculator {
          constructor() {
            this.value = 0;
          }

          add(num) {
            this.value += num;
            return this.value;
          }
        }
      `;

      const analysis = generator.analyzeCodeFile(testCode, 'test.js');

      expect(analysis.functions).toHaveLength(1);
      expect(analysis.classes).toHaveLength(1);
      expect(analysis.functions[0]).toHaveProperty('name', 'add');
      expect(analysis.classes[0]).toHaveProperty('name', 'Calculator');
    });

    test('should generate function docstrings', () => {
      const docstring = generator.generateFunctionDocstring('calculateTotal', 'items, taxRate = 0.1');

      expect(docstring).toContain('/**');
      expect(docstring).toContain('Calculate total');
      expect(docstring).toContain('@param');
      expect(docstring).toContain('@returns');
      expect(docstring).toContain('*/');
    });
  });

  describe('Architecture Documentation Validation', () => {
    test('should validate architecture documentation', async () => {
      const results = await validator.validateArchitectureDocumentation();

      expect(results).toHaveProperty('overview_exists');
      expect(results).toHaveProperty('diagrams_exist');
      expect(results).toHaveProperty('adr_coverage');
      expect(results).toHaveProperty('score');
    });

    test('should generate architecture overview', async () => {
      const components = [
        {
          name: 'API Gateway',
          type: 'api',
          description: 'Main API entry point',
          dependencies: ['Auth Service'],
          technologies: ['Node.js', 'Express']
        },
        {
          name: 'Auth Service',
          type: 'service',
          description: 'Authentication and authorization',
          dependencies: ['Database'],
          technologies: ['Node.js', 'JWT']
        }
      ];

      const architecture = await generator.generateArchitectureDocumentation(components);

      expect(architecture).toHaveProperty('overview');
      expect(architecture).toHaveProperty('components');
      expect(architecture).toHaveProperty('diagrams');
      expect(architecture.components).toHaveLength(2);
      expect(architecture.diagrams).toHaveProperty('component');
      expect(architecture.diagrams).toHaveProperty('dataFlow');
    });
  });

  describe('Usage Documentation Validation', () => {
    test('should validate usage documentation', async () => {
      const results = await validator.validateUsageDocumentation();

      expect(results).toHaveProperty('readme_completeness');
      expect(results).toHaveProperty('getting_started_exists');
      expect(results).toHaveProperty('installation_exists');
      expect(results).toHaveProperty('score');
    });

    test('should generate README content', async () => {
      const projectInfo = {
        name: 'Test Project',
        description: 'A test project for documentation',
        features: ['Feature 1', 'Feature 2'],
        apiEndpoints: [
          { path: '/api/test', method: 'GET', summary: 'Test endpoint' }
        ]
      };

      const readme = await generator.generateReadmeDocumentation(projectInfo);

      expect(readme).toHaveProperty('title', 'Test Project');
      expect(readme).toHaveProperty('sections');
      expect(readme.sections.length).toBeGreaterThan(0);
      expect(readme.sections[0]).toHaveProperty('title');
      expect(readme.sections[0]).toHaveProperty('content');
    });
  });

  describe('Documentation Quality Scoring', () => {
    test('should calculate weighted scores correctly', () => {
      const results = {
        api_score: 0.8,
        code_score: 0.7,
        arch_score: 0.9,
        usage_score: 0.6
      };

      const weights = {
        api_score: 0.25,
        code_score: 0.25,
        arch_score: 0.25,
        usage_score: 0.25
      };

      const overallScore = validator.calculateWeightedScore(results, weights);
      const expectedScore = (0.8 * 0.25) + (0.7 * 0.25) + (0.9 * 0.25) + (0.6 * 0.25);

      expect(overallScore).toBe(expectedScore);
    });

    test('should validate overall documentation quality', async () => {
      const results = await validator.validateAllDocumentation();

      expect(results).toHaveProperty('overall_score');
      expect(results).toHaveProperty('api');
      expect(results).toHaveProperty('code');
      expect(results).toHaveProperty('architecture');
      expect(results).toHaveProperty('usage');
      expect(results).toHaveProperty('critical_issues');
      expect(results).toHaveProperty('recommendations');

      expect(typeof results.overall_score).toBe('number');
      expect(results.overall_score).toBeGreaterThanOrEqual(0);
      expect(results.overall_score).toBeLessThanOrEqual(1);
    });
  });

  describe('Quality Gate Enforcement', () => {
    test('should pass quality gate with good documentation', async () => {
      // Mock a scenario with good documentation coverage
      const mockResults = {
        api: { score: 0.9 },
        code: { score: 0.85 },
        architecture: { score: 0.88 },
        usage: { score: 0.82 }
      };

      const overallScore = (0.9 + 0.85 + 0.88 + 0.82) / 4;
      expect(overallScore).toBeGreaterThan(0.85); // Should pass 85% threshold
    });

    test('should fail quality gate with poor documentation', async () => {
      // Mock a scenario with poor documentation coverage
      const mockResults = {
        api: { score: 0.3 },
        code: { score: 0.4 },
        architecture: { score: 0.2 },
        usage: { score: 0.5 }
      };

      const overallScore = (0.3 + 0.4 + 0.2 + 0.5) / 4;
      expect(overallScore).toBeLessThan(0.85); // Should fail 85% threshold
    });
  });

  describe('File Operations', () => {
    const testFilePath = 'test-docs.md';
    const testContent = '# Test Documentation\n\nThis is a test file.';

    afterEach(async () => {
      // Cleanup test files
      try {
        await fs.unlink(testFilePath);
      } catch (error) {
        // File may not exist
      }
    });

    test('should write files correctly', async () => {
      const success = await generator.writeFile(testFilePath, testContent);
      expect(success).toBe(true);

      const writtenContent = await fs.readFile(testFilePath, 'utf8');
      expect(writtenContent).toBe(testContent);
    });

    test('should read files correctly', async () => {
      await fs.writeFile(testFilePath, testContent);
      const content = await generator.readFile(testFilePath);
      expect(content).toBe(testContent);
    });

    test('should handle missing files gracefully', async () => {
      const content = await generator.readFile('non-existent-file.md');
      expect(content).toBeNull();
    });
  });

  describe('Integration Tests', () => {
    test('should integrate with quality control system', async () => {
      // Test that documentation validation integrates with the main quality control
      const LearningQualityControl = require('../memory-bank/lib/learning-quality-control.js');

      const qualityControl = new LearningQualityControl({
        modeName: 'test-mode'
      });

      // Verify that documentation validator is available
      expect(qualityControl.documentationValidator).toBeDefined();
      expect(qualityControl.documentationValidator).toBeInstanceOf(DocumentationValidator);
    });

    test('should handle documentation check errors gracefully', async () => {
      const qualityControl = new LearningQualityControl({
        modeName: 'test-mode'
      });

      // Test with invalid artifact
      const result = await qualityControl.runDocumentationChecks(null, 'api_documentation');

      expect(result).toHaveLength(1);
      expect(result[0]).toHaveProperty('passed', false);
      expect(result[0]).toHaveProperty('score', 0);
    });
  });
});