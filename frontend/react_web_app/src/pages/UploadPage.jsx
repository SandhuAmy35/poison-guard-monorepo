import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Database, Cpu, Activity } from 'lucide-react';

const UploadPage = () => {
  const navigate = useNavigate();
  const [domain, setDomain] = useState('upi');
  const [isUploading, setIsUploading] = useState(false);
  const [datasetFile, setDatasetFile] = useState(null);
  const [modelFile, setModelFile] = useState(null);
  const datasetRef = useRef(null);
  const modelRef = useRef(null);

  const handleUpload = async () => {
    setIsUploading(true);
    try {
      const formData = new FormData();
      if (datasetFile) formData.append('dataset', datasetFile);
      if (modelFile) formData.append('model', modelFile);
      formData.append('domain', domain);
      
      const response = await fetch('http://localhost:8000/api/ingest', { method: 'POST', body: formData });
      if (!response.ok) throw new Error("Backend non-200");
      // Go to Processing Animation Page
      navigate('/processing', { state: { fallbackToMock: false } });
    } catch (error) {
      console.warn("Backend unavailable. Mock Mode.");
      // Go to Processing Animation Page
      setTimeout(() => navigate('/processing', { state: { fallbackToMock: true } }), 500);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-6 animate-in fade-in duration-1000 z-10 relative">
      <div className="max-w-xl w-full bg-[#1A1D23]/80 backdrop-blur-xl border border-white/10 rounded-2xl p-10 shadow-2xl relative">
        <div className="text-center mb-10">
          <p className="tracking-[0.2em] text-[10px] text-slate-400 uppercase mb-2">Step 01</p>
          <h2 className="text-2xl font-light text-white tracking-wide">Data Ingestion Protocol</h2>
        </div>
        <input type="file" accept=".csv" ref={datasetRef} className="hidden" onChange={(e) => setDatasetFile(e.target.files[0])} />
        <input type="file" accept=".pkl,.h5,.onnx" ref={modelRef} className="hidden" onChange={(e) => setModelFile(e.target.files[0])} />

        <div className="grid grid-cols-2 gap-4 mb-8">
          <div onClick={() => datasetRef.current.click()} className={`border border-white/10 rounded-xl p-8 text-center cursor-pointer transition-all duration-300 ${datasetFile ? 'bg-[#00E5FF]/10 border-[#00E5FF]/50 shadow-[0_0_15px_rgba(0,229,255,0.1)]' : 'bg-black/20 hover:bg-white/5'}`}>
            <Database className={`w-6 h-6 mx-auto mb-3 stroke-1 ${datasetFile ? 'text-[#00E5FF]' : 'text-slate-500'}`} />
            <p className="font-light text-xs tracking-wider text-slate-300">{datasetFile ? datasetFile.name : 'Dataset (.csv)'}</p>
          </div>
          <div onClick={() => modelRef.current.click()} className={`border border-white/10 rounded-xl p-8 text-center cursor-pointer transition-all duration-300 ${modelFile ? 'bg-[#00E5FF]/10 border-[#00E5FF]/50 shadow-[0_0_15px_rgba(0,229,255,0.1)]' : 'bg-black/20 hover:bg-white/5'}`}>
            <Cpu className={`w-6 h-6 mx-auto mb-3 stroke-1 ${modelFile ? 'text-[#00E5FF]' : 'text-slate-500'}`} />
            <p className="font-light text-xs tracking-wider text-slate-300">{modelFile ? modelFile.name : 'Model (.pkl)'}</p>
          </div>
        </div>

        <div className="mb-10">
          <p className="tracking-[0.2em] text-[10px] text-slate-400 uppercase mb-4 text-center">Threat Domain Profile</p>
          <div className="grid grid-cols-2 gap-4">
            <button onClick={() => setDomain('upi')} className={`p-4 rounded-xl border transition-all duration-300 ${domain === 'upi' ? 'border-[#00E5FF]/50 bg-[#00E5FF]/20 text-white shadow-[0_0_15px_rgba(0,229,255,0.2)]' : 'border-white/10 text-slate-400 bg-black/20 hover:bg-white/5'}`}>
              <h3 className="font-light text-sm tracking-wide">UPI Fraud Detection</h3>
            </button>
            <button onClick={() => setDomain('credit')} className={`p-4 rounded-xl border transition-all duration-300 ${domain === 'credit' ? 'border-[#00E5FF]/50 bg-[#00E5FF]/20 text-white shadow-[0_0_15px_rgba(0,229,255,0.2)]' : 'border-white/10 text-slate-400 bg-black/20 hover:bg-white/5'}`}>
              <h3 className="font-light text-sm tracking-wide">Credit Scoring</h3>
            </button>
          </div>
        </div>

        <button onClick={handleUpload} disabled={isUploading} className="w-full py-4 bg-white/90 hover:bg-white text-black tracking-widest uppercase text-xs font-semibold rounded-xl transition-all shadow-[0_0_20px_rgba(255,255,255,0.2)] flex justify-center items-center gap-2">
          {isUploading ? <Activity className="w-4 h-4 animate-spin" /> : 'Initiate Sequence'}
        </button>
      </div>
    </div>
  );
};

export default UploadPage;