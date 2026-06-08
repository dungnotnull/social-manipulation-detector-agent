const API_BASE = 'http://localhost:8000';
const BATCH_INTERVAL_MS = 2000;
const CACHE_TTL_HOURS = 24;

let pendingComments = [];
let batchTimer = null;

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  switch (message.type) {
    case 'ANALYZE_COMMENT':
      handleAnalyzeComment(message.data, message.platform, sendResponse);
      return true;

    case 'GET_CACHED_VERDICT':
      getCachedVerdict(message.commentHash).then(sendResponse);
      return true;

    case 'GET_STATS':
      fetchStats().then(sendResponse);
      return true;

    case 'REPORT_FALSE_POSITIVE':
      reportFalsePositive(message.data).then(sendResponse);
      return true;

    default:
      sendResponse({ error: 'Unknown message type' });
  }
});

function handleAnalyzeComment(data, platform, sendResponse) {
  const batchItem = { data, platform, sendResponse };
  pendingComments.push(batchItem);

  if (!batchTimer) {
    batchTimer = setTimeout(flushBatch, BATCH_INTERVAL_MS);
  }

  const hash = hashText(data.text);
  getCachedVerdict(hash).then((cached) => {
    if (cached) {
      pendingComments = pendingComments.filter((c) => c !== batchItem);
      sendResponse(cached);
    }
  });
}

async function flushBatch() {
  const batch = [...pendingComments];
  pendingComments = [];
  batchTimer = null;

  if (batch.length === 0) return;

  const comments = batch.map((item) => ({
    id: item.data.id || '',
    text: item.data.text,
    author_id: item.data.author_id || '',
    timestamp: item.data.timestamp || '',
  }));

  try {
    const threadId = batch[0].data.thread_id || '';
    const platform = batch[0].platform || 'unknown';

    const response = await fetch(`${API_BASE}/analyze/thread`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ comments, platform, thread_id: threadId }),
    });

    if (!response.ok) {
      batch.forEach((item) => item.sendResponse({ error: `API error: ${response.status}` }));
      return;
    }

    const result = await response.json();
    const verdicts = result.verdicts || [];

    batch.forEach((item, index) => {
      const verdict = verdicts[index] || { manipulation_index: 0, level: 'CLEAN' };
      cacheVerdict(hashText(item.data.text), verdict);
      item.sendResponse(verdict);
    });
  } catch (error) {
    batch.forEach((item) => item.sendResponse({ error: error.message }));
  }
}

async function getCachedVerdict(hash) {
  try {
    const data = await chrome.storage.local.get(`verdict:${hash}`);
    const cached = data[`verdict:${hash}`];
    if (!cached) return null;

    const age = Date.now() - cached.timestamp;
    if (age > CACHE_TTL_HOURS * 3600 * 1000) {
      await chrome.storage.local.remove(`verdict:${hash}`);
      return null;
    }

    return cached.verdict;
  } catch (error) {
    return null;
  }
}

async function cacheVerdict(hash, verdict) {
  try {
    await chrome.storage.local.set({
      [`verdict:${hash}`]: {
        verdict,
        timestamp: Date.now(),
      },
    });
  } catch (error) {
    // Storage may be full — silently skip caching
  }
}

async function fetchStats() {
  try {
    const response = await fetch(`${API_BASE}/campaigns/active`);
    const campaigns = await response.json();
    return { campaigns };
  } catch (error) {
    return { campaigns: [], error: error.message };
  }
}

async function reportFalsePositive(data) {
  try {
    const response = await fetch(`${API_BASE}/feedback/false-positive`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return await response.json();
  } catch (error) {
    return { error: error.message };
  }
}

function hashText(text) {
  let hash = 0;
  for (let i = 0; i < text.length; i++) {
    const char = text.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash |= 0;
  }
  return String(Math.abs(hash));
}
