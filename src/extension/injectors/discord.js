// Discord Web DOM injection
const DISCORD_SELECTORS = {
  messageContainer: '[id^="message-content-"]',
  messageText: '[id^="message-content-"]',
  messageWrapper: '[class*="message"]',
};

function detectDiscordComments() {
  const messages = document.querySelectorAll(DISCORD_SELECTORS.messageContainer);
  const results = [];

  messages.forEach((msg, index) => {
    const text = msg.textContent.trim();
    if (text.length >= 10 && text.length <= 2000) {
      results.push({
        id: `discord-${index}-${Date.now()}`,
        text,
        element: msg.closest('li') || msg,
        platform: 'discord',
      });
    }
  });

  return results;
}

window.detectDiscordComments = detectDiscordComments;
