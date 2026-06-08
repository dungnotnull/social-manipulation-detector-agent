// Facebook DOM injection
const FACEBOOK_SELECTORS = {
  commentContainer: '[role="article"] div[dir="auto"]',
  commentArea: '[role="article"]',
};

function detectFacebookComments() {
  const articles = document.querySelectorAll(FACEBOOK_SELECTORS.commentArea);
  const results = [];

  articles.forEach((article, index) => {
    const textEls = article.querySelectorAll('div[dir="auto"]');
    if (textEls.length === 0) return;

    const text = Array.from(textEls)
      .map((el) => el.textContent.trim())
      .join(' ');

    if (text.length >= 10 && text.length <= 2000) {
      results.push({
        id: `facebook-${index}-${Date.now()}`,
        text,
        element: textEls[0],
        platform: 'facebook',
      });
    }
  });

  return results;
}

window.detectFacebookComments = detectFacebookComments;
