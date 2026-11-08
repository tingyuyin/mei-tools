// 看一段 DSH 会话的上下文用量（不依赖任何插件，只读会话日志）。
// 日志在 ~/.dsh/sessions/*/session*/session.v4.jsonl.zstd，多帧 zstd，流式解。
//
// 用法：
//   node ctx-usage.js                # 取最近改动的那个会话日志
//   node ctx-usage.js <log.zstd>     # 指定日志
const fs = require('fs');
const path = require('path');
const os = require('os');
const zlib = require('zlib');
const readline = require('readline');
const { pipeline } = require('stream/promises');

function newestLog() {
  const root = path.join(os.homedir(), '.dsh', 'sessions');
  let best = null;
  for (const ws of fs.readdirSync(root)) {
    const p = path.join(root, ws);
    if (!fs.statSync(p).isDirectory()) continue;
    for (const s of fs.readdirSync(p)) {
      const f = path.join(p, s, 'session.v4.jsonl.zstd');
      if (!fs.existsSync(f)) continue;
      const m = fs.statSync(f).mtimeMs;
      if (!best || m > best.m) best = { f, m };
    }
  }
  return best && best.f;
}

async function main() {
  const src = process.argv[2] || newestLog();
  if (!src) { console.error('找不到会话日志'); process.exit(1); }
  const tmp = path.join(os.tmpdir(), 'ctx-usage-' + process.pid + '.jsonl');
  await pipeline(fs.createReadStream(src), zlib.createZstdDecompress(), fs.createWriteStream(tmp));

  const rl = readline.createInterface({ input: fs.createReadStream(tmp), crlfDelay: Infinity });
  const rows = [];
  let ctx = {};
  for await (const line of rl) {
    if (!line) continue;
    let o; try { o = JSON.parse(line); } catch (e) { continue; }
    if (o.type === 'request/context' && o.data) {
      if (typeof o.data.contextWindow === 'number') ctx.contextWindow = o.data.contextWindow;
      if (o.data.model) ctx.model = o.data.model;
      if (o.data.provider) ctx.provider = o.data.provider;
    }
    if (o.type === 'assistant/message' && o.data && o.data.usage) {
      const u = o.data.usage;
      rows.push({
        t: o.time, turn: o.data.turn, step: o.data.step,
        prompt: (u.inputTokens || 0) + (u.cacheReadTokens || 0),
        cache: u.cacheReadTokens || 0,
      });
    }
  }
  fs.unlink(tmp, () => {});

  if (!rows.length) { console.log('这段日志里没有用量记录'); return; }
  const hhmm = (ms) => new Date(ms).toTimeString().slice(0, 5);
  const last = rows[rows.length - 1];
  const first = rows[0];
  console.log(`日志：${path.basename(path.dirname(path.dirname(src)))}`);
  console.log(`模型：${ctx.model || '?'}（${ctx.provider || '?'}），窗口 ${ctx.contextWindow ? ctx.contextWindow.toLocaleString() : '未知'}`);
  console.log(`步数 ${rows.length}，从 ${hhmm(first.t)} 到 ${hhmm(last.t)}`);
  const pct = ctx.contextWindow ? (last.prompt / ctx.contextWindow * 100).toFixed(1) + '%' : '—';
  console.log(`当前提示词 ≈ ${last.prompt.toLocaleString()} tokens（缓存 ${last.cache.toLocaleString()} + 新增 ${(last.prompt - last.cache).toLocaleString()}），占窗口 ${pct}`);
  console.log(`起点 ${first.prompt.toLocaleString()}，涨了 ${(last.prompt - first.prompt).toLocaleString()}`);

  const perTurn = new Map();
  for (const r of rows) perTurn.set(r.turn, r);
  const turns = [...perTurn.values()];
  console.log('\n最近若干轮（轮号 时间 提示词 tokens）：');
  for (const r of turns.slice(-8)) {
    console.log(`  turn${String(r.turn).padStart(3)} ${hhmm(r.t)}  ${r.prompt.toLocaleString()}`);
  }
  let biggest = null;
  for (let i = 1; i < turns.length; i++) {
    const d = turns[i].prompt - turns[i - 1].prompt;
    if (!biggest || d > biggest.d) biggest = { d, turn: turns[i].turn };
  }
  if (biggest) console.log(`\n单轮涨得最多：turn${biggest.turn} +${biggest.d.toLocaleString()}`);
}
main();
