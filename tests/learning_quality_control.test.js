const test = require('node:test');
const assert = require('node:assert/strict');
const Module = require('module');
const originalLoad = Module._load;
Module._load = (request, parent, isMain) => {
  if (request === 'ajv') return class Ajv {};
  if (request === 'ajv-formats') return () => {};
  return originalLoad(request, parent, isMain);
};
const LearningQualityControl = require('../memory-bank/lib/learning-quality-control');

// Utility to create instance with stubbed dependencies
function createControl() {
  const qc = new LearningQualityControl({ modeName: 'test' });
  qc.learningClient.getLearningGuidance = async () => ({ available: false });
  qc.workflowHelpers.postTaskLearningUpdate = async () => ({ success: true });
  return qc;
}

test('runQualityGate orchestrates checks and logs metrics', async () => {
  const qc = createControl();
  const result = await qc.runQualityGate('const a = 1;');
  assert.equal(result.gate_type, 'general');
  const metrics = qc.qualityMetrics.get('test_general');
  assert.ok(metrics, 'metrics should be logged');
  assert.equal(result.passed, false);
});

test('runQualityGate handles invalid gate type', async () => {
  const qc = createControl();
  const result = await qc.runQualityGate('artifact', 123);
  assert.equal(result.passed, false);
  assert.equal(result.error_type, 'QualityGateError');
});
