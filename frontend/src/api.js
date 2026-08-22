// Django REST API랑 통신하는 헬퍼예요.
// vite.config.js의 proxy 설정 덕분에 /api, /accounts는 Django(8000)로 그대로 전달돼요.
// 그래서 브라우저 입장에선 계속 같은 origin(5173)에만 접속하는 걸로 보이고,
// 로그인 세션 쿠키/CSRF도 별도 CORS 설정 없이 그대로 동작해요.

function getCsrfToken() {
  const match = document.cookie.match(/csrftoken=([^;]+)/);
  return match ? match[1] : '';
}

/**
 * fetch를 감싸서 401/403(로그인 필요)이면 자동으로 Django 로그인 페이지로 보내요.
 * 로그인 성공하면 Django가 next 파라미터(여기선 '/')로 다시 이 앱으로 돌려보내줘요.
 */
async function apiFetch(url, options = {}) {
  const response = await fetch(url, {
    ...options,
    headers: {
      ...(options.headers || {}),
      ...(options.method && options.method !== 'GET' ? { 'X-CSRFToken': getCsrfToken() } : {}),
    },
  });

  if (response.status === 401 || response.status === 403) {
    window.location.href = '/accounts/login/?next=/';
    // 리다이렉트가 실제로 일어나기 전까지 나머지 코드가 실행되지 않도록 막아요.
    return new Promise(() => {});
  }

  return response;
}

export async function fetchMe() {
  const res = await apiFetch('/api/me/');
  if (!res.ok) throw new Error('사용자 정보를 불러오지 못했어요.');
  return res.json();
}

export async function fetchScanResults(category) {
  const res = await apiFetch(`/api/scan-results/?category=${category}`);
  if (!res.ok) throw new Error('스캔 결과를 불러오지 못했어요.');
  return res.json();
}

export async function runCloudScan() {
  const res = await apiFetch('/api/scan/cloud/', { method: 'POST' });
  if (!res.ok) throw new Error('클라우드 스캔 요청에 실패했어요: ' + res.status);
  return res.json();
}

export async function runCodeScan() {
  const res = await apiFetch('/api/scan/code/', { method: 'POST' });
  if (!res.ok) throw new Error('코드 스캔 요청에 실패했어요: ' + res.status);
  return res.json();
}

export async function runPhishingScan(input) {
  const res = await apiFetch('/api/scan/phishing/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ input }),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.error || '피싱 검사 요청에 실패했어요: ' + res.status);
  }
  return res.json();
}

export async function logout() {
  await apiFetch('/accounts/logout/', { method: 'POST' });
  window.location.href = '/accounts/login/?next=/';
}
