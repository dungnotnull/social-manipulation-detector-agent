document.addEventListener('DOMContentLoaded', () => {
  loadCampaigns();
  loadSettings();

  document.getElementById('refresh-btn').addEventListener('click', loadCampaigns);

  document.getElementById('sensitivity').addEventListener('change', saveSettings);
  document.getElementById('show-clean').addEventListener('change', saveSettings);

  const platformToggles = document.querySelectorAll('.platform-toggles input');
  platformToggles.forEach((toggle) => {
    toggle.addEventListener('change', saveSettings);
  });
});

async function loadCampaigns() {
  const list = document.getElementById('campaign-list');

  try {
    const response = await fetch('http://localhost:8000/campaigns/active');
    const campaigns = await response.json();

    if (!campaigns || campaigns.length === 0) {
      list.innerHTML = '<p class="empty">No active campaigns detected</p>';
      return;
    }

    list.innerHTML = campaigns
      .map(
        (c) => `
      <div class="campaign-item">
        <div class="campaign-name">${escapeHtml(c.name)}</div>
        <div class="campaign-meta">
          <span class="platform-tag">${escapeHtml(c.platform)}</span>
          <span>${c.account_count} accounts</span>
          <span>${escapeHtml(c.tactic_category || 'Unknown')}</span>
        </div>
      </div>
    `
      )
      .join('');
  } catch (error) {
    list.innerHTML = '<p class="error">Cannot reach API. Ensure server is running on port 8000.</p>';
  }
}

async function loadSettings() {
  const data = await chrome.storage.local.get(['sensitivity', 'showClean', 'platforms']);

  if (data.sensitivity) {
    document.getElementById('sensitivity').value = data.sensitivity;
  }
  if (data.showClean !== undefined) {
    document.getElementById('show-clean').checked = data.showClean;
  }
  if (data.platforms) {
    const platforms = data.platforms;
    document.getElementById('platform-twitter').checked = platforms.twitter !== false;
    document.getElementById('platform-reddit').checked = platforms.reddit !== false;
    document.getElementById('platform-youtube').checked = platforms.youtube !== false;
    document.getElementById('platform-facebook').checked = platforms.facebook === true;
  }
}

async function saveSettings() {
  const settings = {
    sensitivity: document.getElementById('sensitivity').value,
    showClean: document.getElementById('show-clean').checked,
    platforms: {
      twitter: document.getElementById('platform-twitter').checked,
      reddit: document.getElementById('platform-reddit').checked,
      youtube: document.getElementById('platform-youtube').checked,
      facebook: document.getElementById('platform-facebook').checked,
    },
  };

  await chrome.storage.local.set(settings);
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}
