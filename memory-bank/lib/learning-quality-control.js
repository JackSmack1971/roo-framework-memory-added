const fs = require('fs/promises');
const path = require('path');
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
    const metrics = {
      mode: this.modeName,
      gate_type: gateType,
      overall_score: 0,
      passed: false,
      check_count: 1,
      learning_enhanced: false,
      timestamp: new Date().toISOString()
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
        score: 0
      }
    ];
  }
}

module.exports = LearningQualityControl;
