// Reddit DOM injection
const REDDIT_SELECTORS = {
  commentContainer: 'shreddit-comment',
  commentText: '[slot="comment"]',
  commentHeader: '.flex.items-start',
};

function detectRedditComments() {
  const comments = document.querySelectorAll(REDDIT_SELECTORS.commentContainer);
  const results = [];

  comments.forEach((comment, index) => {
    const textEl = comment.querySelector(REDDIT_SELECTORS.commentText);
    const text = textEl ? textEl.textContent.trim() : '';
    if (text.length >= 10 && text.length <= 2000) {
      const header = comment.querySelector(REDDIT_SELECTORS.commentHeader);
      results.push({
        id: `reddit-${index}-${Date.now()}`,
        text,
        element: header || comment,
        platform: 'reddit',
      });
    }
  });

  return results;
}

window.detectRedditComments = detectRedditComments;
