// Telegram Web DOM injection
const TELEGRAM_SELECTORS = {
  messageContainer: '.Message',
  messageText: '.Message .text-content',
  messageBubble: '.bubble-content',
};

function detectTelegramComments() {
  const messages = document.querySelectorAll(TELEGRAM_SELECTORS.messageContainer);
  const results = [];

  messages.forEach((msg, index) => {
    const textEl = msg.querySelector(TELEGRAM_SELECTORS.messageText);
    const text = textEl ? textEl.textContent.trim() : '';
    if (text.length >= 10 && text.length <= 2000) {
      results.push({
        id: `telegram-${index}-${Date.now()}`,
        text,
        element: msg,
        platform: 'telegram',
      });
    }
  });

  return results;
}

window.detectTelegramComments = detectTelegramComments;
