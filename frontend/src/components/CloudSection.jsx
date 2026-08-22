import { useState } from 'react';
import ResultsTable, { StatusBadge } from './ResultsTable';
import { runCloudScan } from '../api';

const COLUMNS = [
  { key: 'target', label: '대상' },
  { key: 'status', label: '상태', render: (item) => <StatusBadge isRisky={item.is_risky} /> },
  { key: 'detail', label: '상세' },
  { key: 'ai_explanation', label: 'AI 설명', className: 'explanation' },
  { key: 'scanned_at', label: '스캔 시각' },
];

function CloudSection({ results, onScanDone }) {
  const [scanning, setScanning] = useState(false);
  const riskyCount = results.filter((r) => r.is_risky).length;

  async function handleScan() {
    setScanning(true);
    try {
      await runCloudScan();
      await onScanDone();
    } catch (err) {
      alert(err.message);
    } finally {
      setScanning(false);
    }
  }

  return (
    <section>
      <h2 className="section-title">☁️ 클라우드 인프라 (S3 / IAM / 보안 그룹)</h2>
      <div className="summary">
        <div className="card">
          <div>전체 점검 항목 수</div>
          <h2>{results.length}개</h2>
        </div>
        <div className="card danger">
          <div>위험 발견 수</div>
          <h2>{riskyCount}개</h2>
        </div>
      </div>
      <button type="button" className="scan-btn" disabled={scanning} onClick={handleScan}>
        {scanning ? '스캔 중... (AI 설명 생성에 시간이 걸릴 수 있어요)' : '🔍 클라우드 스캔 실행 (S3+IAM+SG)'}
      </button>
      <ResultsTable
        columns={COLUMNS}
        rows={results}
        emptyMessage="아직 스캔 결과가 없습니다. 위 버튼을 눌러 스캔을 실행하세요."
      />
    </section>
  );
}

export default CloudSection;
