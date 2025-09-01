const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs/promises');
const path = require('path');
const os = require('os');
process.env.NODE_PATH = path.join(__dirname, '..', 'node_modules');
require('module').Module._initPaths();
const LearningProtocolClient = require('../memory-bank/lib/learning-protocol-client');

async function setupClient() {
  const tmp = await fs.mkdtemp(path.join(os.tmpdir(), 'learning-client-'));
  await fs.cp(path.join(__dirname, '..', 'memory-bank'), path.join(tmp, 'memory-bank'), {
    recursive: true
  });
  // stub pattern-storage to avoid heavy dependencies
  const stub = `class Store {\n  async getRecommendedPatterns() { return []; }\n  async updatePatternStats() { return { metadata: { usage_statistics: {} } }; }\n}\nmodule.exports = Store;`;
  await fs.writeFile(
    path.join(tmp, 'memory-bank', 'lib', 'pattern-storage.js'),
    stub
  );
  const client = new LearningProtocolClient({ learningSystemPath: path.join(tmp, 'memory-bank') });
  return { client, tmp };
}

test('logOutcome appends success and failure counts', async () => {
  const { client, tmp } = await setupClient();
  const logFile = path.join(tmp, 'decisionLog.md');
  await client.logOutcome('test-mode', 'unit', 'success', 0.9, 'demo');
  const content = await fs.readFile(logFile, 'utf8');
  assert.match(content, /Successful Applications:/);
  assert.match(content, /Failed Applications:/);
});

test('getLearningGuidance retries before succeeding', async () => {
  const { client } = await setupClient();
  let calls = 0;
  client.queryLearningSystem = async () => {
    calls += 1;
    if (calls < 3) throw new Error('temporary');
    return { available: true, guidance: { recommendations: [], recommended_patterns: [] }, metadata: {} };
  };
  const res = await client.getLearningGuidance({}, 'unit');
  assert.equal(calls, 3);
  assert.equal(res.available, true);
});

test('getLearningGuidance throws LearningApiError after timeouts', async () => {
  const { client } = await setupClient();
  client.options.timeoutMs = 50;
  let calls = 0;
  client.queryLearningSystem = async () => {
    calls += 1;
    await new Promise(res => setTimeout(res, 100));
    return { available: true, guidance: { recommendations: [], recommended_patterns: [] }, metadata: {} };
  };
  await assert.rejects(
    () => client.getLearningGuidance({}, 'unit'),
    err => err instanceof LearningProtocolClient.LearningApiError
  );
  assert.equal(calls, client.options.retries);
});

