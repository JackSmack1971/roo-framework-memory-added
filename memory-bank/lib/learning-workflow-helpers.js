const fs = require('fs/promises');
const path = require('path');
const PatternStorage = require('./pattern-storage');

class LearningWorkflowHelpers {
  constructor(options = {}) {
    this.modeName = options.modeName || 'default';
    const psOptions = options.patternStorageOptions || {};
    this.patternStorage = new PatternStorage(psOptions);
  }

  async updatePatternOutcome(pattern, success) {
    const updated = await this.patternStorage.updatePatternStats(pattern.id, success);
    if (typeof updated.confidence_score !== 'number') updated.confidence_score = 0.5;
    const delta = success ? 0.1 : -0.05;
    updated.confidence_score = Math.max(
      0.1,
      Math.min(0.95, parseFloat((updated.confidence_score + delta).toFixed(2)))
    );
    this.patternStorage.patterns.set(pattern.id, updated);
    return updated;
  }

  async createQualityTask(warning, context = {}) {
    if (!warning) throw new Error('Invalid warning');
    const file = process.env.WORKFLOW_STATE_PATH;
    let data = {};
    if (file) {
      try {
        data = JSON.parse(await fs.readFile(file, 'utf8'));
      } catch {
        data = {};
      }
    }
    if (!Array.isArray(data.active_tasks)) data.active_tasks = [];
    const id = `task_${Date.now()}`;
    data.active_tasks.push({ task_id: id, objective: warning, context });
    if (file) await fs.writeFile(file, JSON.stringify(data, null, 2));
    return id;
  }

  async postTaskLearningUpdate() {
    return { success: true };
  }
}

module.exports = LearningWorkflowHelpers;
