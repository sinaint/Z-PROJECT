import { useState } from 'react';
import ResultsTable, { formatScannedAt } from './ResultsTable';
import { runCodeScan } from '../api';

const COLUMNS = [
  { key: 'target', label: '파일 위치' },
  { key: 'detail', label: '상세', className: 'explanation' },
  { key: 'ai_explanation', label: 'AI 설명', className: 'explanation' },
  { key: 'scanned_at', label: '스캔 시각', render: (item) => formatScannedAt(item.scanned_at) },
];

function CodeSection({ results, onScanDone }) {
  const [scanning, setScanning] = useState(false);

  async function handleScan() {
    setScanning(true);
    try {
      await runCodeScan();
      await onScanDone();
    } catch (err) {
      alert(err.message);
    } finally {
      setScanning(false);
    }
  }

  return (
    <section>
      <h2 className="section-title">🧑‍💻 코드 (하드코딩된 시크릿)</h2>
      <div className="summary">
        <div className="card danger">
          <div>발견된 시크릿 수</div>
          <h2>{results.length}개</h2>
        </div>
      </div>
      <button type="button" className="scan-btn" disabled={scanning} onClick={handleScan}>
        {scanning ? '스캔 중... (AI 설명 생성에 시간이 걸릴 수 있어요)' : '🔍 코드 스캔 실행'}
      </button>
      <ResultsTable
        columns={COLUMNS}
        rows={results}
        emptyMessage="아직 스캔 결과가 없습니다. 위 버튼을 눌러 스캔을 실행하세요."
      />
    </section>
  );
}

export default CodeSection;
