const fs = require('fs/promises');
const path = require('path');

class PatternStorage {
  constructor(options = {}) {
    this.storagePath = options.storagePath || path.join(__dirname, '..', 'data');
    this.schemaPath = options.schemaPath || path.join(__dirname, '..', 'schemas', 'pattern-schema.json');
    this.patterns = new Map();
  }

  async initialize() {
    const data = await fs.readFile(path.join(this.storagePath, 'actionable-patterns.json'), 'utf8');
    const patterns = JSON.parse(data);
    for (const p of patterns) {
      this.patterns.set(p.id, p);
    }
  }

  validatePattern(pattern) {
    return typeof pattern.id === 'string' && typeof pattern.metadata === 'object';
  }

  async getPattern(id) {
    return this.patterns.get(id);
  }

  async updatePatternStats(id, success) {
    const pattern = this.patterns.get(id);
    if (!pattern.metadata) pattern.metadata = {};
    if (!pattern.metadata.usage_statistics) {
      pattern.metadata.usage_statistics = {
        total_applications: 0,
        successful_applications: 0,
        failed_applications: 0
      };
    }
    const stats = pattern.metadata.usage_statistics;
    stats.total_applications += 1;
    if (success) stats.successful_applications += 1;
    else stats.failed_applications += 1;
    pattern.success_rate = stats.total_applications
      ? stats.successful_applications / stats.total_applications
      : 0;
    return pattern;
  }

  async getRecommendedPatterns() {
    return Array.from(this.patterns.values());
  }
}

module.exports = PatternStorage;
