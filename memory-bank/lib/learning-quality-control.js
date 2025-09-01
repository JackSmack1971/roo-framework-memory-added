const fs = require('fs/promises');
const path = require('path');
const yaml = require('js-yaml');
const LearningProtocolClient = require('./learning-protocol-client');
const LearningWorkflowHelpers = require('./learning-workflow-helpers');
const DocumentationValidator = require('./documentation-validator');

class LearningQualityControl {
  constructor(options = {}) {
    this.modeName = options.modeName || 'default';
    this.learningClient = new LearningProtocolClient({ learningSystemPath: path.join(__dirname, '..') });
    this.workflowHelpers = new LearningWorkflowHelpers({ modeName: this.modeName });
    this.documentationValidator = new DocumentationValidator();
    this.qualityMetrics = new Map();
  }

  async runQualityGate(artifact, gateType = 'general') {
    if (typeof gateType !== 'string') {
      return { passed: false, error_type: 'QualityGateError' };
    }
    const key = `${this.modeName}_${gateType}`;
    const checks = await this.runDocumentationChecks(artifact, gateType);
    const checkCount = checks.length;
    const overallScore =
      checks.reduce((sum, c) => sum + (c.score || 0), 0) / (checkCount || 1);
    const threshold = await this.getQualityThreshold(gateType);
    const passed = checks.every(c => c.passed) && overallScore >= threshold;
    const metrics = {
      mode: this.modeName,
      gate_type: gateType,
      overall_score: overallScore,
      passed,
      threshold,
      check_count: checkCount,
      learning_enhanced: false,
      timestamp: new Date().toISOString(),
    };
    this.qualityMetrics.set(key, metrics);
    return metrics;
  }

  async detectQualityAnomalies(metrics) {
    if (
      typeof metrics?.gate_type !== 'string' ||
      typeof metrics?.overall_score !== 'number' ||
      typeof metrics?.timestamp !== 'string'
    ) {
      throw new Error('Invalid metrics input');
    }
    const key = `${this.modeName}_${metrics.gate_type}`;
    const prev = this.qualityMetrics.get(key);
    if (!prev || Math.abs(prev.overall_score - metrics.overall_score) < 0.1) {
      return false;
    }
    const dashPath = process.env.QUALITY_DASHBOARD_PATH;
    if (dashPath) {
      let data = {};
      try {
        data = JSON.parse(await fs.readFile(dashPath, 'utf8'));
      } catch {
        data = {};
      }
      if (!Array.isArray(data.predictive_quality_indicators)) {
        data.predictive_quality_indicators = [];
      }
      data.predictive_quality_indicators.push({ ...metrics, mode: this.modeName });
      await fs.writeFile(dashPath, JSON.stringify(data, null, 2));
    }
    return await this.workflowHelpers.createQualityTask('quality anomaly', metrics);
  }

  async runDocumentationChecks(artifact, type) {
    return [
      {
        check: type || 'documentation',
        passed: false,
        score: 0,
      },
    ];
  }

  async getQualityThreshold(gateType) {
    const defaultThreshold = 0.8;
    const root = process.cwd();
    try {
      const rulesPath = path.join(root, '.roo', 'rules', `${gateType}.json`);
      const data = JSON.parse(await fs.readFile(rulesPath, 'utf8'));
      if (typeof data.threshold === 'number') return data.threshold;
    } catch {}
    try {
      const roomodes = yaml.load(
        await fs.readFile(path.join(root, '.roomodes'), 'utf8'),
      );
      const t =
        roomodes?.qualityGate?.thresholds?.[gateType] ??
        roomodes?.qualityGate?.default;
      if (typeof t === 'number') return t;
    } catch {}
    return defaultThreshold;
  }
}

module.exports = LearningQualityControl;
