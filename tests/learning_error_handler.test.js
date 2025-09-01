const test = require('node:test');
const assert = require('node:assert/strict');
const LearningErrorHandler = require('../memory-bank/lib/learning-error-handler');

test('loadGlobalPatternsGuide reads global patterns file', async () => {
  const handler = new LearningErrorHandler({ modeName: 'test' });
  const content = await handler.loadGlobalPatternsGuide();
  assert.ok(content.includes('Global Patterns'));
});

test('default fallback references global patterns', async () => {
  const handler = new LearningErrorHandler({ modeName: 'test' });
  const result = await handler.fallbackModes.get('default').execute({}, 'operation');
  assert.match(result.guidance.fallback_advice, /global-patterns\.md/);
});
