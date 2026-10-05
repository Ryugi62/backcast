const assert = require('assert');
const { backcast } = require('./backcast');
const D = Date.UTC(2026, 9, 5, 3, 45); // 12:45 KST
const steps = [{ name: 'Build', minutes: 60 }, { name: 'Video', minutes: 30, optional: true }, { name: 'Submit', minutes: 10 }];
// on track: now = 2h before deadline
let r = backcast(D, steps, D - 120 * 60000, 0);
assert.strictEqual(r.plan[0].startMs, D - 100 * 60000);
assert.strictEqual(r.plan[2].endMs, D);
assert.strictEqual(r.status, 'start-now');
assert.strictEqual(r.slackMin, 20);
// late: now = 80 min before, need 100 -> cut Video (optional)
r = backcast(D, steps, D - 80 * 60000, 0);
assert.strictEqual(r.status, 'late');
assert.deepStrictEqual(r.cut, ['Video']);
assert.strictEqual(r.stillShortMin, 0);
// very late: cuts are not enough -> honest remaining shortfall
r = backcast(D, steps, D - 40 * 60000, 0);
assert.strictEqual(r.stillShortMin, 30);
// buffer 50% grows durations
r = backcast(D, steps, D - 1000 * 60000, 50);
assert.strictEqual(r.plan[0].minutes, 90);
console.log('all tests passed (4 scenarios)');
