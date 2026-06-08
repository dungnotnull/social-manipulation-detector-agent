// YouTube DOM injection
const YOUTUBE_SELECTORS = {
  commentRenderer: 'ytd-comment-renderer',
  commentText: '#content-text',
  commentHeader: '#header',
};

function detectYoutubeComments() {
  const comments = document.querySelectorAll(YOUTUBE_SELECTORS.commentRenderer);
  const results = [];

  comments.forEach((comment, index) => {
    const textEl = comment.querySelector(YOUTUBE_SELECTORS.commentText);
    const text = textEl ? textEl.textContent.trim() : '';
    if (text.length >= 10 && text.length <= 2000) {
      const header = comment.querySelector(YOUTUBE_SELECTORS.commentHeader);
      results.push({
        id: `youtube-${index}-${Date.now()}`,
        text,
        element: header || comment,
        platform: 'youtube',
      });
    }
  });

  return results;
}

window.detectYoutubeComments = detectYoutubeComments;
