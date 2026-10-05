// Backcast core: pure scheduling logic (no DOM, no I/O).
// Given a deadline and ordered steps with durations (minutes), plan backward:
// each step's latest start = next step's latest start - its duration.
function backcast(deadlineMs, steps, nowMs, bufferPct) {
  const buf = 1 + (bufferPct || 0) / 100;
  let end = deadlineMs;
  const plan = [];
  for (let i = steps.length - 1; i >= 0; i--) {
    const dur = Math.round(steps[i].minutes * buf) * 60000;
    const start = end - dur;
    plan.unshift({ name: steps[i].name, startMs: start, endMs: end, minutes: Math.round(steps[i].minutes * buf) });
    end = start;
  }
  const startBy = plan.length ? plan[0].startMs : deadlineMs;
  const slackMin = Math.floor((startBy - nowMs) / 60000);
  let status = 'on-track';
  if (slackMin < 0) status = 'late';
  else if (slackMin < 30) status = 'start-now';
  // what to cut if late: drop the longest optional steps until it fits
  const cut = [];
  let stillShortMin = 0;
  if (status === 'late') {
    let need = -slackMin;
    const opt = steps.map((s, i) => ({ ...s, i })).filter(s => s.optional).sort((a, b) => b.minutes - a.minutes);
    for (const s of opt) { if (need <= 0) break; cut.push(s.name); need -= Math.round(s.minutes * buf); }
    stillShortMin = Math.max(0, need);
  }
  return { plan, startByMs: startBy, slackMin, status, cut, stillShortMin };
}
if (typeof module !== 'undefined') module.exports = { backcast };
