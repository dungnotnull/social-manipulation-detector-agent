const PLATFORM_CONFIG = {
  twitter: {
    selector: 'article[data-testid="tweet"]',
    textSelector: '[data-testid="tweetText"]',
    injectPoint: '[data-testid="tweetText"]',
    commentIdAttr: 'data-tweet-id',
  },
  reddit: {
    selector: 'shreddit-comment',
    textSelector: '[slot="comment"]',
    injectPoint: 'shreddit-comment',
  },
  youtube: {
    selector: 'ytd-comment-renderer',
    textSelector: '#content-text',
    injectPoint: '#header',
  },
  facebook: {
    selector: '[role="article"] div[dir="auto"]',
    textSelector: null,
    injectPoint: null,
  },
};

const LEVEL_STYLES = {
  HIGH: { badge: '🔴', label: 'MANIPULATION DETECTED', className: 'smda-badge-high' },
  ELEVATED: { badge: '🟠', label: 'SUSPICIOUS', className: 'smda-badge-elevated' },
  MODERATE: { badge: '🟡', label: 'LOW RISK', className: 'smda-badge-moderate' },
  LOW: { badge: '🔵', label: 'MINOR SIGNALS', className: 'smda-badge-low' },
  CLEAN: { badge: '', label: '', className: 'smda-badge-clean' },
};

function detectPlatform() {
  const hostname = window.location.hostname;
  if (hostname.includes('twitter.com') || hostname.includes('x.com')) return 'twitter';
  if (hostname.includes('reddit.com')) return 'reddit';
  if (hostname.includes('youtube.com')) return 'youtube';
  if (hostname.includes('facebook.com')) return 'facebook';
  return null;
}

function extractComments(platform) {
  const config = PLATFORM_CONFIG[platform];
  if (!config) return [];

  const elements = document.querySelectorAll(config.selector);
  const comments = [];

  elements.forEach((el, index) => {
    const textEl = config.textSelector ? el.querySelector(config.textSelector) : el;
    const text = textEl ? textEl.textContent.trim() : '';
    if (text.length >= 10 && text.length <= 2000) {
      comments.push({
        id: `${platform}-${index}-${Date.now()}`,
        text,
        element: el,
        platform,
      });
    }
  });

  return comments;
}

async function analyzeComments(comments) {
  const results = await Promise.all(
    comments.map((comment) => {
      return new Promise((resolve) => {
        const hash = hashCommentText(comment.text);
        chrome.runtime.sendMessage(
          { type: 'GET_CACHED_VERDICT', commentHash: hash },
          (cached) => {
            if (cached) {
              resolve({ ...comment, verdict: cached });
            } else {
              chrome.runtime.sendMessage(
                {
                  type: 'ANALYZE_COMMENT',
                  data: {
                    id: comment.id,
                    text: comment.text,
                    author_id: '',
                    thread_id: window.location.href,
                  },
                },
                (verdict) => {
                  resolve({ ...comment, verdict });
                }
              );
            }
          }
        );
      });
    })
  );
  return results;
}

function injectBadge(comment, verdict) {
  const level = verdict.level || 'CLEAN';
  const style = LEVEL_STYLES[level] || LEVEL_STYLES.CLEAN;

  if (level === 'CLEAN') return;

  const existing = comment.element.querySelector('.smda-badge');
  if (existing) existing.remove();

  const badge = document.createElement('div');
  badge.className = `smda-badge ${style.className}`;
  badge.innerHTML = `
    <span class="smda-badge-icon">${style.badge}</span>
    <span class="smda-badge-label">${style.label}</span>
    <span class="smda-badge-score">${(verdict.manipulation_index * 100).toFixed(0)}%</span>
  `;

  badge.addEventListener('click', () => showEvidencePanel(comment, verdict));

  const injectEl = comment.element;
  if (injectEl && injectEl.parentNode) {
    injectEl.parentNode.insertBefore(badge, injectEl);
  }
}

function showEvidencePanel(comment, verdict) {
  let panel = document.getElementById('smda-evidence-panel');
  if (!panel) {
    panel = document.createElement('div');
    panel.id = 'smda-evidence-panel';
    panel.className = 'smda-evidence-panel';
    document.body.appendChild(panel);
  }

  const evidence = verdict.evidence || [];
  const tactics = verdict.tactics_detected || [];

  panel.innerHTML = `
    <div class="smda-panel-header">
      <span>${verdict.summary || 'Manipulation Analysis'}</span>
      <button class="smda-panel-close">&times;</button>
    </div>
    <div class="smda-panel-body">
      <div class="smda-panel-score">
        Manipulation Index: <strong>${(verdict.manipulation_index * 100).toFixed(0)}%</strong>
        <span class="smda-confidence">(${verdict.confidence} confidence)</span>
      </div>
      ${tactics.length > 0 ? `
        <div class="smda-panel-tactics">
          <strong>Tactics detected:</strong>
          <ul>${tactics.map((t) => `<li>${t}</li>`).join('')}</ul>
        </div>
      ` : ''}
      ${evidence.length > 0 ? `
        <div class="smda-panel-evidence">
          <strong>Evidence:</strong>
          ${evidence.map((e) => `
            <div class="smda-evidence-item">
              <span class="smda-evidence-tactic">[${e.tactic}]</span>
              <span class="smda-evidence-span">"${e.span}"</span>
              <p class="smda-evidence-explanation">${e.explanation}</p>
            </div>
          `).join('')}
        </div>
      ` : ''}
      <button class="smda-report-false-positive">Report as False Positive</button>
    </div>
  `;

  panel.querySelector('.smda-panel-close').addEventListener('click', () => {
    panel.remove();
  });

  panel.querySelector('.smda-report-false-positive').addEventListener('click', () => {
    chrome.runtime.sendMessage({
      type: 'REPORT_FALSE_POSITIVE',
      data: {
        comment_hash: hashCommentText(comment.text),
        report_type: 'false_positive',
        reporter_notes: '',
      },
    });
    panel.remove();
  });

  panel.style.display = 'block';
}

function hashCommentText(text) {
  let hash = 0;
  for (let i = 0; i < text.length; i++) {
    const char = text.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash |= 0;
  }
  return String(Math.abs(hash));
}

function injectStyles() {
  if (document.getElementById('smda-styles')) return;

  const style = document.createElement('style');
  style.id = 'smda-styles';
  style.textContent = `
    .smda-badge {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 2px 8px;
      border-radius: 12px;
      font-size: 11px;
      font-weight: 600;
      cursor: pointer;
      margin: 4px 0;
      user-select: none;
    }
    .smda-badge-high { background: #fee2e2; color: #991b1b; border: 1px solid #fca5a5; }
    .smda-badge-elevated { background: #ffedd5; color: #9a3412; border: 1px solid #fdba74; }
    .smda-badge-moderate { background: #fef9c3; color: #854d0e; border: 1px solid #fde047; }
    .smda-badge-low { background: #dbeafe; color: #1e40af; border: 1px solid #93c5fd; }
    .smda-badge-score { font-variant-numeric: tabular-nums; }
    .smda-badge:hover { opacity: 0.85; }

    .smda-evidence-panel {
      display: none;
      position: fixed;
      bottom: 20px;
      right: 20px;
      width: 400px;
      max-height: 500px;
      background: white;
      border: 1px solid #e5e7eb;
      border-radius: 12px;
      box-shadow: 0 10px 40px rgba(0,0,0,0.15);
      z-index: 999999;
      overflow: hidden;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    .smda-panel-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px 16px;
      background: #f9fafb;
      border-bottom: 1px solid #e5e7eb;
      font-weight: 600;
    }
    .smda-panel-close {
      background: none;
      border: none;
      font-size: 20px;
      cursor: pointer;
      color: #6b7280;
    }
    .smda-panel-body {
      padding: 16px;
      overflow-y: auto;
      max-height: 420px;
    }
    .smda-panel-score {
      margin-bottom: 12px;
      font-size: 16px;
    }
    .smda-confidence { color: #6b7280; font-size: 12px; }
    .smda-panel-tactics { margin-bottom: 12px; }
    .smda-panel-tactics ul { margin: 4px 0 0 16px; }
    .smda-panel-tactics li { font-size: 13px; color: #374151; }
    .smda-evidence-item {
      margin-bottom: 8px;
      padding: 8px;
      background: #f9fafb;
      border-radius: 6px;
    }
    .smda-evidence-tactic {
      font-weight: 600;
      font-size: 12px;
      color: #991b1b;
    }
    .smda-evidence-span {
      font-style: italic;
      font-size: 13px;
      color: #374151;
    }
    .smda-evidence-explanation {
      margin: 4px 0 0;
      font-size: 12px;
      color: #6b7280;
    }
    .smda-report-false-positive {
      width: 100%;
      padding: 8px;
      background: #f3f4f6;
      border: 1px solid #d1d5db;
      border-radius: 6px;
      cursor: pointer;
      font-size: 13px;
      margin-top: 8px;
    }
    .smda-report-false-positive:hover { background: #e5e7eb; }
  `;
  document.head.appendChild(style);
}

function observeAndAnalyze() {
  const platform = detectPlatform();
  if (!platform) return;

  injectStyles();

  const observer = new MutationObserver(() => {
    const comments = extractComments(platform);
    if (comments.length > 0) {
      analyzeComments(comments).then((results) => {
        results.forEach((result) => {
          if (result.verdict && !result.verdict.error) {
            injectBadge(result, result.verdict);
          }
        });
      });
    }
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true,
  });

  const comments = extractComments(platform);
  if (comments.length > 0) {
    analyzeComments(comments).then((results) => {
      results.forEach((result) => {
        if (result.verdict && !result.verdict.error) {
          injectBadge(result, result.verdict);
        }
      });
    });
  }
}

observeAndAnalyze();
