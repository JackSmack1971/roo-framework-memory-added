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

test('runQualityGate passes when checks meet threshold', async () => {
  const qc = createControl();
  qc.runDocumentationChecks = async () => [
    { check: 'doc', passed: true, score: 0.9 },
  ];
  const result = await qc.runQualityGate('artifact');
  assert.equal(result.passed, true);
  assert.equal(result.overall_score, 0.9);
});

test('runQualityGate fails when average below threshold', async () => {
  const qc = createControl();
  qc.runDocumentationChecks = async () => [
    { check: 'doc', passed: true, score: 0.7 },
  ];
  const result = await qc.runQualityGate('artifact');
  assert.equal(result.passed, false);
  assert.equal(result.overall_score, 0.7);
});

test('runQualityGate passes at threshold edge case', async () => {
  const qc = createControl();
  qc.runDocumentationChecks = async () => [
    { check: 'a', passed: true, score: 0.9 },
    { check: 'b', passed: true, score: 0.7 },
  ];
  const result = await qc.runQualityGate('artifact');
  assert.equal(result.overall_score, 0.8);
  assert.equal(result.passed, true);
});
