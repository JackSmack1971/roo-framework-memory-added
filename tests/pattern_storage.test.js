const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs/promises');
const path = require('path');
const os = require('os');
const PatternStorage = require('../memory-bank/lib/pattern-storage');

async function setupStorage() {
  const tmp = await fs.mkdtemp(path.join(os.tmpdir(), 'pattern-storage-'));
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
  const storage = new PatternStorage({
    storagePath: dataDir,
    schemaPath: path.join(schemaDir, 'pattern-schema.json')
  });
  await storage.initialize();
  return storage;
}

test('updatePatternStats tracks success and failure', async () => {
  const storage = await setupStorage();
  const id = 'auth_mechanism_undefined_v1';
  const original = JSON.parse(JSON.stringify(await storage.getPattern(id)));

  const afterSuccess = JSON.parse(
    JSON.stringify(await storage.updatePatternStats(id, true))
  );
  assert.equal(
    afterSuccess.metadata.usage_statistics.total_applications,
    original.metadata.usage_statistics.total_applications + 1
  );
  assert.equal(
    afterSuccess.metadata.usage_statistics.successful_applications,
    original.metadata.usage_statistics.successful_applications + 1
  );
  assert.equal(
    afterSuccess.metadata.usage_statistics.failed_applications,
    original.metadata.usage_statistics.failed_applications
  );
  assert.ok(
    Math.abs(
      afterSuccess.success_rate -
        afterSuccess.metadata.usage_statistics.successful_applications /
          afterSuccess.metadata.usage_statistics.total_applications
    ) < 1e-6
  );

  const afterFailure = await storage.updatePatternStats(id, false);
  const failureCopy = JSON.parse(JSON.stringify(afterFailure));
  assert.equal(
    failureCopy.metadata.usage_statistics.total_applications,
    afterSuccess.metadata.usage_statistics.total_applications + 1
  );
  assert.equal(
    failureCopy.metadata.usage_statistics.successful_applications,
    afterSuccess.metadata.usage_statistics.successful_applications
  );
  assert.equal(
    failureCopy.metadata.usage_statistics.failed_applications,
    afterSuccess.metadata.usage_statistics.failed_applications + 1
  );
  assert.ok(
    Math.abs(
      failureCopy.success_rate -
        failureCopy.metadata.usage_statistics.successful_applications /
          failureCopy.metadata.usage_statistics.total_applications
    ) < 1e-6
  );
});

test('pattern records validate against schema with usage statistics', async () => {
  const storage = await setupStorage();
  for (const pattern of storage.patterns.values()) {
    assert.ok(storage.validatePattern(pattern));
    const stats = pattern.metadata?.usage_statistics || {};
    assert.equal(typeof stats.successful_applications, 'number');
    assert.equal(typeof stats.failed_applications, 'number');
  }
});
