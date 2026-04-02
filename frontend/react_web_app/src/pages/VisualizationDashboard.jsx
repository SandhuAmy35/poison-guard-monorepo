import React, { useState, useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, Cell } from 'recharts';
import { Download, Activity, Play, RefreshCw } from 'lucide-react';

const mockUmapData = Array.from({ length: 200 }, (_, i) => ({
  x: Math.random() * 80 - 40, y: Math.random() * 80 - 40,
  type: i < 15 ? 'poisoned' : 'clean', id: `SMPL-${1000 + i}`,
  risk: i < 15 ? (Math.random() * 0.5 + 0.5).toFixed(2) : (Math.random() * 0.1).toFixed(2)
}));

const mockInfluenceData = Array.from({ length: 15 }, (_, i) => ({
  id: `SMPL-INF-${i}`, score: (100 - i * 5) + Math.random() * 5,
})).sort((a, b) => b.score - a.score);

const VisualizationDashboard = () => {
  const location = useLocation();
  const fallbackToMock = location.state?.fallbackToMock || false;

  const [telemetry, setTelemetry] = useState({ ingestion_rate: "0 MB/s", cuda_utilization: "0%", active_threats: 0 });
  const [originalUmapData, setOriginalUmapData] = useState([]); 
  const [umapData, setUmapData] = useState([]); 
  const [isSimulating, setIsSimulating] = useState(false);
  const isSimulatingRef = useRef(false); 
  const [influenceData, setInfluenceData] = useState([]);
  const [tableData, setTableData] = useState([]);

  useEffect(() => {
    if (fallbackToMock) {
      setOriginalUmapData(mockUmapData);
      if (!isSimulatingRef.current) setUmapData(mockUmapData);
      setInfluenceData(mockInfluenceData); 
      setTelemetry({ ingestion_rate: "1.2 GB/s", cuda_utilization: "42%", active_threats: 15 });
    } else {
      const ws = new WebSocket('ws://localhost:8000/ws/dashboard');
      ws.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          if (payload.type === 'TELEMETRY_UPDATE') {
            setTelemetry(payload.data);
            if (payload.data.influence_scores) setInfluenceData(payload.data.influence_scores);
            if (payload.data.umap_points) {
              setOriginalUmapData(payload.data.umap_points);
              if (!isSimulatingRef.current) setUmapData(payload.data.umap_points);
            }
          }
        } catch (e) {}
      };
      ws.onerror = () => { 
        setOriginalUmapData(mockUmapData); 
        if (!isSimulatingRef.current) setUmapData(mockUmapData); 
        setInfluenceData(mockInfluenceData); 
        setTelemetry({ ingestion_rate: "1.2 GB/s", cuda_utilization: "42%", active_threats: 15 }); 
      };
      return () => ws.close();
    }
  }, [fallbackToMock]);

  useEffect(() => { 
    setTableData(originalUmapData.filter(d => d.type === 'poisoned').map((d, i) => ({ ...d, reason: ['Z-Score Anomaly', 'Spectral Signature', 'Activation Cluster Outlier'][i % 3] }))); 
  }, [originalUmapData]);

  const handleDownload = () => {
    const csv = "Sample ID,Risk Score,Flag Reason\n" + tableData.map(r => `${r.id},${r.risk},${r.reason}`).join("\n");
    const link = document.createElement("a"); link.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv' })); link.download = "suspected_poison_samples.csv"; link.click();
  };

  const handleSimulate = () => {
    setIsSimulating(true);
    isSimulatingRef.current = true;
    const separatedData = originalUmapData.map(d => {
      if (d.type === 'poisoned') return { ...d, x: 70 + Math.random() * 20, y: 70 + Math.random() * 20 };
      else return { ...d, x: -50 - Math.random() * 40, y: -50 - Math.random() * 40 };
    });
    setUmapData(separatedData);
  };

  const handleHeal = () => {
    setIsSimulating(false);
    isSimulatingRef.current = false;
    setUmapData(originalUmapData);
  };

  return (
    <div className="min-h-screen p-6 relative animate-in fade-in duration-1000 z-10">
      <div className="max-w-7xl mx-auto pt-4">
        
        {/* HEADER */}
        <header className="flex justify-between items-center mb-8 pb-4 border-b border-white/10">
          <div>
            <h1 className="text-2xl font-medium tracking-wide text-white flex items-center gap-3">
              AI PoisonGuard
              {fallbackToMock && <span className="ml-2 text-[10px] bg-amber-500/20 text-amber-400 px-2 py-0.5 rounded border border-amber-500/30 tracking-widest font-bold uppercase">MOCK MODE</span>}
            </h1>
          </div>
          <div className="text-xs text-rose-400 font-mono tracking-widest flex items-center gap-2 bg-rose-500/10 px-4 py-2 rounded-full border border-rose-500/20 font-bold">
            <Activity className="w-4 h-4 animate-pulse" /> THREATS ISOLATED: {telemetry.active_threats}
          </div>
        </header>

        {/* --- MAIN ML CHARTS --- */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          
          {/* UMAP SCATTER PLOT */}
          <div className="bg-[#1A1D23]/80 backdrop-blur-xl border border-white/10 rounded-2xl p-6 flex flex-col">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-[11px] font-bold tracking-[0.2em] text-slate-300 uppercase flex items-center gap-3">
                <span className="w-1.5 h-1.5 rounded-full bg-[#00E5FF] shadow-[0_0_8px_#00E5FF]"></span>Cluster Visualisation
              </h2>
              <div className="flex gap-2">
                <button 
                  onClick={handleSimulate} disabled={isSimulating}
                  className={`flex items-center gap-2 px-3 py-1.5 rounded text-[10px] uppercase tracking-widest font-bold transition-all ${isSimulating ? 'bg-rose-500/10 text-rose-500/50 border border-rose-500/10 cursor-not-allowed' : 'bg-rose-500/20 text-rose-400 hover:bg-rose-500/30 border border-rose-500/30 shadow-[0_0_10px_rgba(244,63,94,0.2)]'}`}
                >
                  <Play className="w-3 h-3" /> Simulate Attack
                </button>
                <button 
                  onClick={handleHeal} disabled={!isSimulating}
                  className={`flex items-center gap-2 px-3 py-1.5 rounded text-[10px] uppercase tracking-widest font-bold transition-all ${!isSimulating ? 'bg-[#00E5FF]/10 text-[#00E5FF]/50 border border-[#00E5FF]/10 cursor-not-allowed' : 'bg-[#00E5FF]/20 text-[#00E5FF] hover:bg-[#00E5FF]/30 border border-[#00E5FF]/30 shadow-[0_0_10px_rgba(0,229,255,0.2)]'}`}
                >
                  <RefreshCw className={`w-3 h-3 ${isSimulating ? 'animate-spin-slow' : ''}`} /> Heal
                </button>
              </div>
            </div>
            
            <div className="flex-1 w-full min-h-[320px]">
              <ResponsiveContainer width="100%" height="100%">
                <ScatterChart margin={{ top: 10, right: 10, bottom: 10, left: 10 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" vertical={false} />
                  <XAxis type="number" dataKey="x" hide domain={[-100, 100]} />
                  <YAxis type="number" dataKey="y" hide domain={[-100, 100]} />
                  <Tooltip cursor={{ strokeDasharray: '3 3' }} contentStyle={{ backgroundColor: 'rgba(26, 29, 35, 0.9)', backdropFilter: 'blur(8px)', borderColor: '#2D3139', borderRadius: '8px', color: '#f8fafc', fontSize: '12px' }} />
                  <Scatter name="Clean" data={umapData.filter(d => d.type === 'clean')} fill="#00E5FF" fillOpacity={0.4} animationDuration={1000} />
                  <Scatter name="Poisoned" data={umapData.filter(d => d.type === 'poisoned')} fill="#fb7185" animationDuration={1000} />
                </ScatterChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* INFLUENCE SCORE BAR CHART */}
          <div className="bg-[#1A1D23]/80 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
            <h2 className="text-[11px] font-bold tracking-[0.2em] text-slate-300 uppercase mb-6 flex items-center gap-3">
              <span className="w-1.5 h-1.5 rounded-full bg-rose-500 shadow-[0_0_8px_#fb7185]"></span>Influence Score
            </h2>
            <div className="h-80 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={influenceData} layout="vertical" margin={{ top: 5, right: 10, left: 40, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" horizontal={false} />
                  <XAxis type="number" stroke="#475569" tick={{ fontSize: 10, fill: '#94a3b8' }} />
                  <YAxis dataKey="id" type="category" stroke="#475569" tick={{ fontSize: 10, fill: '#94a3b8', fontFamily: 'monospace' }} />
                  <Tooltip cursor={{fill: '#ffffff05'}} contentStyle={{ backgroundColor: 'rgba(26, 29, 35, 0.9)', backdropFilter: 'blur(8px)', borderColor: '#2D3139', borderRadius: '8px', color: '#f8fafc', fontSize: '12px' }} />
                  <Bar dataKey="score" radius={[0, 4, 4, 0]} barSize={12}>
                    {influenceData.map((entry, index) => <Cell key={`cell-${index}`} fill={index < 3 ? '#fb7185' : '#475569'} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 pb-10">
          
          {/* LABEL HEATMAP */}
          <div className="bg-[#1A1D23]/80 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
            <h2 className="text-[11px] font-bold tracking-[0.2em] text-slate-300 uppercase mb-6 flex items-center gap-3">
              <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 shadow-[0_0_8px_#6366f1]"></span>Label Heatmap
            </h2>
            <div className="h-64 w-full grid grid-cols-8 gap-1.5">
              {Array.from({ length: 64 }).map((_, i) => (
                <div key={`heat-${i}`} className={`rounded-sm transition-colors duration-1000 ${[12, 13, 20, 21, 45].includes(i) ? 'bg-rose-500/80 animate-pulse shadow-[0_0_15px_rgba(244,63,94,0.4)]' : 'bg-[#00E5FF]/20'}`} style={{ opacity: [12, 13, 20, 21, 45].includes(i) ? 1 : Math.random() * 0.4 + 0.1 }}></div>
              ))}
            </div>
          </div>

          {/* DATA TABLE */}
          <div className="bg-[#1A1D23]/80 backdrop-blur-xl border border-white/10 rounded-2xl p-6 flex flex-col max-h-[350px]">
            <div className="flex justify-between items-start mb-6">
              <h2 className="text-[11px] font-bold tracking-[0.2em] text-slate-300 uppercase flex items-center gap-3">
                <span className="w-1.5 h-1.5 rounded-full bg-slate-300"></span>Flagged Samples
              </h2>
              <button onClick={handleDownload} className="px-4 py-2 bg-black/40 hover:bg-white/10 rounded-lg text-[10px] font-bold tracking-widest uppercase transition-colors border border-white/10 flex items-center gap-2 text-slate-300">
                <Download className="w-3 h-3" /> Export
              </button>
            </div>
            <div className="flex-1 overflow-auto pr-2 custom-scrollbar">
              <table className="w-full text-left text-sm font-light">
                <thead className="text-slate-400 sticky top-0 bg-[#1A1D23]/95 backdrop-blur-md z-10">
                  <tr>
                    <th className="pb-4 text-[10px] font-bold tracking-widest uppercase">ID</th>
                    <th className="pb-4 text-[10px] font-bold tracking-widest uppercase">Risk</th>
                    <th className="pb-4 text-[10px] font-bold tracking-widest uppercase">Reason</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {tableData.map((row, idx) => (
                    <tr key={`row-${idx}`} className="hover:bg-white/5 transition-colors group">
                      <td className="py-3 text-slate-200 font-mono text-xs">{row.id}</td>
                      <td className="py-3">
                        <span className="text-rose-400 bg-rose-400/10 px-2 py-1 rounded shadow-[0_0_8px_rgba(251,113,133,0.1)] text-xs font-bold">
                          {row.risk}
                        </span>
                      </td>
                      <td className="py-3 text-slate-400 group-hover:text-slate-200 transition-colors text-xs">{row.reason}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VisualizationDashboard;