const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs/promises');
const path = require('path');
const os = require('os');
const LearningWorkflowHelpers = require('../memory-bank/lib/learning-workflow-helpers');

async function setupHelper() {
  const tmp = await fs.mkdtemp(path.join(os.tmpdir(), 'lwh-'));
  const dataDir = path.join(tmp, 'data');
  const schemaDir = path.join(tmp, 'schemas');
  await fs.mkdir(dataDir, { recursive: true });
  await fs.mkdir(schemaDir, { recursive: true });
  await fs.copyFile(
    path.join(__dirname, '..', 'memory-bank', 'data', 'actionable-patterns.json'),
    path.join(dataDir, 'actionable-patterns.json')
  );
  await fs.copyFile(
    path.join(__dirname, '..', 'memory-bank', 'schemas', 'pattern-schema.json'),
    path.join(schemaDir, 'pattern-schema.json')
  );
  const helper = new LearningWorkflowHelpers({
    modeName: 'test-mode',
    patternStorageOptions: {
      storagePath: dataDir,
      schemaPath: path.join(schemaDir, 'pattern-schema.json')
    }
  });
  await helper.patternStorage.initialize();
  return helper;
}

test('confidence adjusts with successes and failures', async () => {
  const helper = await setupHelper();
  const patternId = 'auth_mechanism_undefined_v1';

  for (let i = 0; i < 5; i++) {
    const pattern = await helper.patternStorage.getPattern(patternId);
    await helper.updatePatternOutcome(pattern, true);
  }
  let record = await helper.patternStorage.getPattern(patternId);
  assert.equal(record.confidence_score, 0.95);

  for (let i = 0; i < 20; i++) {
    const pattern = await helper.patternStorage.getPattern(patternId);
    await helper.updatePatternOutcome(pattern, false);
  }
  record = await helper.patternStorage.getPattern(patternId);
  assert.equal(record.confidence_score, 0.1);
});

test('createQualityTask records tasks and returns id', async () => {
  const helper = await setupHelper();
  const tmp = await fs.mkdtemp(path.join(os.tmpdir(), 'wf-'));
  const workflow = path.join(tmp, 'workflow-state.json');
  await fs.writeFile(workflow, '{}');
  process.env.WORKFLOW_STATE_PATH = workflow;
  const id = await helper.createQualityTask('need review', { severity: 'high' });
  const flow = JSON.parse(await fs.readFile(workflow, 'utf8'));
  const task = flow.active_tasks.find(t => t.task_id === id);
  assert.equal(task.objective, 'need review');
  assert.equal(task.context.severity, 'high');
});

test('createQualityTask validates inputs', async () => {
  const helper = await setupHelper();
  await assert.rejects(() => helper.createQualityTask('', {}), /Invalid warning/);
});
