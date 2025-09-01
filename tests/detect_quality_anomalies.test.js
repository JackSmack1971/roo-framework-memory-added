const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs/promises');
const path = require('path');
const os = require('os');
const LearningQualityControl = require('../memory-bank/lib/learning-quality-control');

test('detectQualityAnomalies logs anomalies and creates quality task', async () => {
  const tmp = await fs.mkdtemp(path.join(os.tmpdir(), 'quality-'));
  const dashboard = path.join(tmp, 'quality-dashboard.json');
  const workflow = path.join(tmp, 'workflow-state.json');
  await fs.writeFile(dashboard, '{}');
  await fs.writeFile(workflow, '{}');
  process.env.QUALITY_DASHBOARD_PATH = dashboard;
  process.env.WORKFLOW_STATE_PATH = workflow;
  const qc = new LearningQualityControl({ modeName: 'test' });
  const prev = {
    mode: 'test',
    gate_type: 'general',
    overall_score: 0.9,
    passed: true,
    check_count: 1,
    learning_enhanced: false,
    timestamp: new Date().toISOString()
  };
  qc.qualityMetrics.set('test_general', prev);
  const metrics = {
    gate_type: 'general',
    overall_score: 0.7,
    timestamp: new Date().toISOString()
  };
  const taskId = await qc.detectQualityAnomalies(metrics);
  assert.match(taskId, /^task_\d+/);
  const dash = JSON.parse(await fs.readFile(dashboard, 'utf8'));
  assert.ok(Array.isArray(dash.predictive_quality_indicators));
  const flow = JSON.parse(await fs.readFile(workflow, 'utf8'));
  assert.ok(flow.active_tasks.find(t => t.task_id === taskId));
});

test('detectQualityAnomalies returns false for minor deviations', async () => {
  const qc = new LearningQualityControl({ modeName: 'test' });
  qc.qualityMetrics.set('test_general', {
    gate_type: 'general',
    overall_score: 0.9,
    timestamp: new Date().toISOString()
  });
  const result = await qc.detectQualityAnomalies({
    gate_type: 'general',
    overall_score: 0.85,
    timestamp: new Date().toISOString()
  });
  assert.equal(result, false);
});

test('detectQualityAnomalies rejects invalid metrics', async () => {
  const qc = new LearningQualityControl({ modeName: 'test' });
  await assert.rejects(
    () => qc.detectQualityAnomalies({ gate_type: 1, overall_score: 2 }),
    /Invalid metrics input/
  );
});

