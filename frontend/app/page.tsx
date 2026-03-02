'use client';
import { useEffect, useState } from 'react';
import { getTrends, collectNow, getDashboard, getRegions } from '@/lib/api';

export default function Home() {
  const [trends, setTrends] = useState<any[]>([]);
  const [dashboard, setDashboard] = useState<any>({});
  const [regions, setRegions] = useState<any[]>([]);
  const [region, setRegion] = useState('BR');
  const [loading, setLoading] = useState(false);
  const [collecting, setCollecting] = useState(false);

  useEffect(() => {
    loadData();
    getRegions().then(setRegions);
    getDashboard().then(setDashboard);
  }, [region]);

  async function loadData() {
    setLoading(true);
    const data = await getTrends(region);
    setTrends(data);
    setLoading(false);
  }

  async function handleCollect() {
    setCollecting(true);
    await collectNow(region);
    await loadData();
    const d = await getDashboard();
    setDashboard(d);
    setCollecting(false);
  }

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <header className="bg-gray-900 border-b border-gray-800 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-blue-400">News Intake Dashboard</h1>
            <p className="text-xs text-gray-500">Tendencias e noticias filtradas por fontes aprovadas</p>
          </div>
          <nav className="flex gap-4 text-sm">
            <a href="/" className="text-blue-400 font-semibold">Dashboard</a>
            <a href="/feed" className="text-gray-400 hover:text-white">Feed</a>
            <a href="/sources" className="text-gray-400 hover:text-white">Fontes</a>
            <a href="/admin" className="text-gray-400 hover:text-white">Admin</a>
          </nav>
        </div>
      </header>
      <main className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {[
            { label: 'Tendencias', value: dashboard.total_trends ?? 0, color: 'text-blue-400' },
            { label: 'Artigos', value: dashboard.total_articles ?? 0, color: 'text-green-400' },
            { label: 'Fontes Aprovadas', value: dashboard.approved_sources ?? 0, color: 'text-yellow-400' },
            { label: 'Logs', value: dashboard.total_logs ?? 0, color: 'text-purple-400' },
          ].map((s) => (
            <div key={s.label} className="bg-gray-900 rounded-xl p-4 border border-gray-800">
              <p className="text-xs text-gray-500 mb-1">{s.label}</p>
              <p className={`text-3xl font-bold ${s.color}`}>{s.value}</p>
            </div>
          ))}
        </div>
        <div className="flex items-center gap-4 mb-6">
          <select value={region} onChange={(e) => setRegion(e.target.value)} className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white">
            {regions.map((r) => (<option key={r.code} value={r.code}>{r.name}</option>))}
          </select>
          <button onClick={handleCollect} disabled={collecting} className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 text-white px-4 py-2 rounded-lg text-sm font-medium">
            {collecting ? 'Coletando...' : 'Coletar Agora'}
          </button>
        </div>
        <h2 className="text-lg font-semibold mb-4 text-gray-300">Tendencias</h2>
        {loading ? (
          <p className="text-gray-500 text-sm">Carregando...</p>
        ) : trends.length === 0 ? (
          <div className="bg-gray-900 rounded-xl p-8 text-center border border-gray-800">
            <p className="text-gray-400">Nenhuma tendencia. Clique em Coletar Agora.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {trends.map((trend, i) => (
              <a key={trend.id} href={`/feed?trend=${trend.id}`} className="bg-gray-900 hover:bg-gray-800 border border-gray-800 hover:border-blue-700 rounded-xl p-4 transition-all group">
                <div className="flex items-start gap-3">
                  <span className="text-2xl font-bold text-gray-700 w-8 shrink-0">{i + 1}</span>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-white line-clamp-2">{trend.keyword}</p>
                    <div className="flex items-center gap-3 mt-2">
                      <span className="text-xs text-gray-500">Score: {trend.score?.toFixed(1)}</span>
                    </div>
                  </div>
                  <span className="text-gray-600 text-lg">-&gt;</span>
                </div>
              </a>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
