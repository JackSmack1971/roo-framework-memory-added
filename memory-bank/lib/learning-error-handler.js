const fs = require('fs/promises');
const path = require('path');

class LearningErrorHandler {
  constructor(options = {}) {
    this.modeName = options.modeName || 'default';
    this.globalGuidePath = path.join(__dirname, '..', 'global-patterns.md');
    this.fallbackModes = new Map([
      [
        'default',
        {
          execute: async () => ({
            guidance: {
              fallback_advice: `Refer to global patterns: ${this.globalGuidePath}`
            }
          })
        }
      ]
    ]);
  }

  async loadGlobalPatternsGuide() {
    return fs.readFile(this.globalGuidePath, 'utf8');
  }
}

module.exports = LearningErrorHandler;
