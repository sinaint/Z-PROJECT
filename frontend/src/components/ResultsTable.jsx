// 스캔 결과 표를 그리는 공용 컴포넌트예요.
// columns에 [{key, label, render?}] 형태로 어떤 컬럼을 보여줄지 넘겨주면 돼요.
// render가 있으면 그 함수로, 없으면 그냥 item[key] 값을 그대로 보여줘요.
function ResultsTable({ columns, rows, emptyMessage }) {
  return (
    <table className="results-table">
      <thead>
        <tr>
          {columns.map((col) => (
            <th key={col.key}>{col.label}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {rows.length === 0 ? (
          <tr>
            <td colSpan={columns.length}>{emptyMessage}</td>
          </tr>
        ) : (
          rows.map((item) => (
            <tr key={item.id}>
              {columns.map((col) => (
                <td key={col.key} className={col.className}>
                  {col.render ? col.render(item) : item[col.key] || '-'}
                </td>
              ))}
            </tr>
          ))
        )}
      </tbody>
    </table>
  );
}

// 서버가 주는 ISO 문자열(2026-08-22T12:30:55...)을 Django 템플릿과 비슷한
// 사람이 읽기 편한 형식으로 바꿔줘요.
export function formatScannedAt(value) {
  if (!value) return '-';
  return new Date(value).toLocaleString('ko-KR', {
    year: 'numeric', month: 'short', day: 'numeric',
    hour: 'numeric', minute: '2-digit',
  });
}

export function StatusBadge({ isRisky }) {
  return isRisky ? (
    <span className="status-danger">🚨 위험</span>
  ) : (
    <span className="status-safe">✅ 안전</span>
  );
}

export default ResultsTable;
