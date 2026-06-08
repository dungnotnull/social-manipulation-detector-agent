// Twitter / X.com DOM injection
const TWITTER_SELECTORS = {
  tweetContainer: 'article[data-testid="tweet"]',
  tweetText: '[data-testid="tweetText"]',
  userName: '[data-testid="User-Name"]',
};

function detectTwitterComments() {
  const tweets = document.querySelectorAll(TWITTER_SELECTORS.tweetContainer);
  const comments = [];

  tweets.forEach((tweet, index) => {
    const textEl = tweet.querySelector(TWITTER_SELECTORS.tweetText);
    const text = textEl ? textEl.textContent.trim() : '';
    if (text.length >= 10 && text.length <= 2000) {
      const injectEl = tweet.querySelector(TWITTER_SELECTORS.userName);
      comments.push({
        id: `twitter-${index}-${Date.now()}`,
        text,
        element: injectEl || tweet,
        platform: 'twitter',
      });
    }
  });

  return comments;
}

window.detectTwitterComments = detectTwitterComments;
