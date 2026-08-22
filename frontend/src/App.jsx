import { useEffect, useState, useCallback } from 'react';
import { fetchMe, fetchScanResults, logout } from './api';
import CloudSection from './components/CloudSection';
import CodeSection from './components/CodeSection';
import PhishingSection from './components/PhishingSection';
import './App.css';

function App() {
  const [username, setUsername] = useState(null);
  const [cloudResults, setCloudResults] = useState([]);
  const [codeResults, setCodeResults] = useState([]);
  const [phishingResults, setPhishingResults] = useState([]);
  const [loading, setLoading] = useState(true);

  // 세 영역 결과를 전부 다시 불러와요. (로그인 안 됐으면 api.js가 알아서 로그인 페이지로 보내줘요)
  const reloadAll = useCallback(async () => {
    const [cloud, code, phishing] = await Promise.all([
      fetchScanResults('cloud'),
      fetchScanResults('code'),
      fetchScanResults('phishing'),
    ]);
    setCloudResults(cloud);
    setCodeResults(code);
    setPhishingResults(phishing);
  }, []);

  useEffect(() => {
    async function init() {
      const me = await fetchMe();
      setUsername(me.username);
      await reloadAll();
      setLoading(false);
    }
    init();
  }, [reloadAll]);

  if (loading) {
    return <div className="loading">불러오는 중...</div>;
  }

  return (
    <div className="dashboard">
      <div className="header-row">
        <h1>🛡️ Aegis - AI 보안 코파일럿</h1>
        <div className="logout-form">
          <span className="whoami">{username}님</span>
          <button type="button" className="logout-btn" onClick={logout}>
            로그아웃
          </button>
        </div>
      </div>

      <CloudSection results={cloudResults} onScanDone={reloadAll} />
      <CodeSection results={codeResults} onScanDone={reloadAll} />
      <PhishingSection results={phishingResults} onScanDone={reloadAll} />
    </div>
  );
}

export default App;
