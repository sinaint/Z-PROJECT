import { useState } from 'react';
import ResultsTable, { StatusBadge, formatScannedAt } from './ResultsTable';
import { runPhishingScan } from '../api';

const COLUMNS = [
  { key: 'target', label: '입력값' },
  { key: 'status', label: '상태', render: (item) => <StatusBadge isRisky={item.is_risky} /> },
  { key: 'detail', label: '상세', className: 'explanation' },
  { key: 'ai_explanation', label: 'AI 설명', className: 'explanation' },
  { key: 'scanned_at', label: '스캔 시각', render: (item) => formatScannedAt(item.scanned_at) },
];

function PhishingSection({ results, onScanDone }) {
  const [input, setInput] = useState('');
  const [scanning, setScanning] = useState(false);
  const riskyCount = results.filter((r) => r.is_risky).length;

  async function handleScan() {
    const value = input.trim();
    if (!value) {
      alert('검사할 URL이나 이메일 본문을 입력해주세요.');
      return;
    }

    setScanning(true);
    try {
      await runPhishingScan(value);
      setInput('');
      await onScanDone();
    } catch (err) {
      alert(err.message);
    } finally {
      setScanning(false);
    }
  }

  return (
    <section>
      <h2 className="section-title">🎣 사람 (피싱 URL/이메일)</h2>
      <div className="summary">
        <div className="card danger">
          <div>위험 판정 수</div>
          <h2>{riskyCount}개</h2>
        </div>
      </div>
      <div className="phishing-form">
        <input
          type="text"
          className="phishing-input"
          placeholder="의심스러운 URL이나 이메일 본문을 붙여넣으세요 (예: http://naver.com@evil-login.top)"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleScan()}
        />
        <button type="button" className="scan-btn" disabled={scanning} onClick={handleScan}>
          {scanning ? '검사 중...' : '🔍 피싱 검사 실행'}
        </button>
      </div>
      <ResultsTable
        columns={COLUMNS}
        rows={results}
        emptyMessage="아직 검사한 URL/이메일이 없습니다. 위 입력창에 붙여넣고 검사해보세요."
      />
    </section>
  );
}

export default PhishingSection;
