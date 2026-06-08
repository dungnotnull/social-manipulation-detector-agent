import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 10 },
    { duration: '1m', target: 50 },
    { duration: '1m', target: 200 },
    { duration: '30s', target: 500 },
    { duration: '1m', target: 500 },
    { duration: '30s', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<5000'],
    http_req_failed: ['rate<0.05'],
  },
};

const BASE_URL = 'http://localhost:8000';

const SAMPLE_COMMENTS = [
  { text: "I disagree with this policy because it historically hasn't worked.", platform: 'twitter', thread_id: 'load-test-1', author_id: 'test_1' },
  { text: "Just bought some ETH for the first time. Excited to learn more about the space!", platform: 'twitter', thread_id: 'load-test-1', author_id: 'test_2' },
  { text: "The Fed announcement is tomorrow. Might be volatile, might not.", platform: 'twitter', thread_id: 'load-test-1', author_id: 'test_3' },
  { text: "🚀🚀 This token is about to EXPLODE! Don't miss out on 100x gains!", platform: 'twitter', thread_id: 'load-test-2', author_id: 'test_4' },
  { text: "Absolutely! You've raised such an important point here. I completely agree!", platform: 'twitter', thread_id: 'load-test-2', author_id: 'test_5' },
];

export default function () {
  const comment = SAMPLE_COMMENTS[Math.floor(Math.random() * SAMPLE_COMMENTS.length)];

  const singleRes = http.post(`${BASE_URL}/analyze/text`, JSON.stringify(comment), {
    headers: { 'Content-Type': 'application/json' },
  });
  check(singleRes, {
    'single text status 200': (r) => r.status === 200,
  });

  sleep(0.5);

  const threadPayload = {
    comments: [
      { id: 'c1', text: comment.text, author_id: 'a1', timestamp: new Date().toISOString() },
      { id: 'c2', text: SAMPLE_COMMENTS[0].text, author_id: 'a2', timestamp: new Date().toISOString() },
      { id: 'c3', text: SAMPLE_COMMENTS[3].text, author_id: 'a3', timestamp: new Date().toISOString() },
      { id: 'c4', text: SAMPLE_COMMENTS[2].text, author_id: 'a4', timestamp: new Date().toISOString() },
      { id: 'c5', text: SAMPLE_COMMENTS[1].text, author_id: 'a5', timestamp: new Date().toISOString() },
    ],
    platform: 'twitter',
    thread_id: 'load-test-thread',
  };

  const threadRes = http.post(`${BASE_URL}/analyze/thread`, JSON.stringify(threadPayload), {
    headers: { 'Content-Type': 'application/json' },
  });
  check(threadRes, {
    'thread status 200': (r) => r.status === 200,
  });

  if (Math.random() < 0.3) {
    const healthRes = http.get(`${BASE_URL}/health`);
    check(healthRes, { 'health ok': (r) => r.status === 200 && r.json('status') === 'ok' });
  }

  if (Math.random() < 0.1) {
    http.get(`${BASE_URL}/campaigns/active`);
  }

  sleep(1);
}
