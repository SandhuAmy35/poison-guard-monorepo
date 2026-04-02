import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Hexagon, Link as LinkIcon, ShieldCheck, Server, Database, Network, Zap } from 'lucide-react';
import ShaderBackground from '../components/ShaderBackground';

const ProcessingPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const fallbackToMock = location.state?.fallbackToMock || false;

  const [phase, setPhase] = useState('blockchain'); // 'blockchain' -> 'cpp'
  const [step, setStep] = useState(0);

  useEffect(() => {
    // Phase 1: Blockchain Sequence
    const t1 = setTimeout(() => setStep(1), 500);   // SHA Hash
    const t2 = setTimeout(() => setStep(2), 2000);  // Ledger Sync
    const t3 = setTimeout(() => setStep(3), 3500);  // Verified
    
    // Switch to Phase 2: C++ Ingestion
    const t4 = setTimeout(() => {
      setPhase('cpp');
      setStep(0);
    }, 5000);

    // Phase 2: C++ Sequence
    const t5 = setTimeout(() => setStep(1), 5500);  // MMAP Buffer
    const t6 = setTimeout(() => setStep(2), 7000);  // ZeroMQ Stream
    const t7 = setTimeout(() => setStep(3), 8500);  // Python ML Reached
    
    // Final Redirect to Dashboard
    const t8 = setTimeout(() => {
      navigate('/dashboard', { state: { fallbackToMock } });
    }, 10000);

    return () => { [t1, t2, t3, t4, t5, t6, t7, t8].forEach(clearTimeout); };
  }, [navigate, fallbackToMock]);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-6 relative z-10 overflow-hidden">
      
      {/* THE WEBGL SHADER BACKGROUND (Only on this page!) */}
      <ShaderBackground />
      
      {/* Dark overlay to keep text readable over the bright shader */}
      <div className="absolute inset-0 bg-black/70 z-0"></div>

      {/* PHASE 1: BLOCKCHAIN GATEKEEPER */}
      <div className={`transition-all duration-1000 absolute w-full max-w-4xl flex flex-col items-center z-10 ${phase === 'blockchain' ? 'opacity-100 scale-100' : 'opacity-0 scale-95 pointer-events-none'}`}>
        <h2 className="text-[#00E5FF] tracking-[0.3em] text-sm sm:text-lg uppercase mb-16 font-light drop-shadow-md">Blockchain Gatekeeper Verification</h2>
        
        <div className="flex w-full justify-between items-center relative px-4">
          <div className="absolute top-8 left-14 right-14 h-1 bg-[#2D3139] -z-10 rounded-full overflow-hidden">
            <div className={`h-full bg-gradient-to-r from-[#00E5FF] to-[#34C759] transition-all duration-1000 ease-out`} style={{ width: step >= 3 ? '100%' : step === 2 ? '50%' : '0%' }} />
          </div>

          <div className={`flex flex-col items-center transition-all duration-500 ${step >= 1 ? 'opacity-100 scale-110' : 'opacity-50'}`}>
            <div className={`w-16 h-16 rounded-xl flex items-center justify-center bg-[#1A1D23]/80 backdrop-blur-md border-2 transition-all ${step >= 1 ? 'border-[#00E5FF] shadow-[0_0_20px_rgba(0,229,255,0.4)]' : 'border-[#2D3139]'}`}>
              <Hexagon className={`w-8 h-8 ${step === 1 ? 'text-[#00E5FF] animate-[spin_3s_linear_infinite]' : 'text-slate-500'}`} />
            </div>
            <span className="mt-4 font-mono text-xs text-slate-200">SHA-256 HASH</span>
            <span className="mt-1 font-mono text-[10px] text-[#00E5FF] h-4">{step >= 1 ? '0x4f82...1a9b' : ''}</span>
          </div>

          <div className={`flex flex-col items-center transition-all duration-500 ${step >= 2 ? 'opacity-100 scale-110' : 'opacity-50'}`}>
            <div className={`w-16 h-16 rounded-xl flex items-center justify-center bg-[#1A1D23]/80 backdrop-blur-md border-2 transition-all ${step >= 2 ? 'border-[#00E5FF] shadow-[0_0_20px_rgba(0,229,255,0.4)]' : 'border-[#2D3139]'}`}>
              <LinkIcon className={`w-8 h-8 ${step === 2 ? 'text-[#00E5FF] animate-pulse' : 'text-slate-500'}`} />
            </div>
            <span className="mt-4 font-mono text-xs text-slate-200">LEDGER SYNC</span>
            <span className="mt-1 font-mono text-[10px] text-[#00E5FF] h-4">{step >= 2 ? 'Polygon Amoy' : ''}</span>
          </div>

          <div className={`flex flex-col items-center transition-all duration-500 ${step >= 3 ? 'opacity-100 scale-110' : 'opacity-50'}`}>
            <div className={`w-16 h-16 rounded-xl flex items-center justify-center bg-[#1A1D23]/80 backdrop-blur-md border-2 transition-all ${step >= 3 ? 'border-[#34C759] shadow-[0_0_30px_rgba(52,199,89,0.5)]' : 'border-[#2D3139]'}`}>
              <ShieldCheck className={`w-8 h-8 ${step >= 3 ? 'text-[#34C759]' : 'text-slate-500'}`} />
            </div>
            <span className="mt-4 font-mono text-xs text-[#34C759] font-bold drop-shadow-[0_0_8px_#34C759]">VERIFIED</span>
            <span className="mt-1 font-mono text-[10px] text-[#34C759] h-4">{step >= 3 ? 'Tamper Proof' : ''}</span>
          </div>
        </div>
      </div>

      {/* PHASE 2: C++ INGESTION */}
      <div className={`transition-all duration-1000 absolute w-full max-w-4xl flex flex-col items-center z-10 ${phase === 'cpp' ? 'opacity-100 scale-100' : 'opacity-0 scale-105 pointer-events-none'}`}>
        <h2 className="text-indigo-400 tracking-[0.3em] text-sm sm:text-lg uppercase mb-16 font-light drop-shadow-md">Hardware Accelerated Ingestion (C++17)</h2>
        
        <div className="flex w-full justify-between items-center relative px-4">
          <div className="absolute top-8 left-14 right-14 h-1 bg-[#2D3139] -z-10 rounded-full overflow-hidden">
            <div className="h-full bg-gradient-to-r from-indigo-500 to-rose-500 transition-all duration-1000 ease-out" style={{ width: step >= 3 ? '100%' : step === 2 ? '50%' : '0%' }} />
          </div>

          <div className={`flex flex-col items-center transition-all duration-500 ${step >= 1 ? 'opacity-100 scale-110' : 'opacity-50'}`}>
            <div className={`w-16 h-16 rounded-xl flex items-center justify-center bg-[#1A1D23]/80 backdrop-blur-md border-2 transition-all ${step >= 1 ? 'border-indigo-400 shadow-[0_0_20px_rgba(99,102,241,0.4)]' : 'border-[#2D3139]'}`}>
              <Database className={`w-8 h-8 ${step === 1 ? 'text-indigo-400' : 'text-slate-500'}`} />
            </div>
            <span className="mt-4 font-mono text-xs text-slate-200">MMAP BUFFER</span>
            <span className="mt-1 font-mono text-[10px] text-indigo-400 h-4">{step >= 1 ? 'Zero-Copy Load' : ''}</span>
          </div>

          <div className={`flex flex-col items-center transition-all duration-500 ${step >= 2 ? 'opacity-100 scale-110' : 'opacity-50'}`}>
            <div className={`w-16 h-16 rounded-xl flex items-center justify-center bg-[#1A1D23]/80 backdrop-blur-md border-2 transition-all ${step >= 2 ? 'border-indigo-400 shadow-[0_0_20px_rgba(99,102,241,0.4)]' : 'border-[#2D3139]'}`}>
              <Network className={`w-8 h-8 ${step === 2 ? 'text-indigo-400 animate-pulse' : 'text-slate-500'}`} />
            </div>
            <span className="mt-4 font-mono text-xs text-slate-200">ZeroMQ IPC</span>
            <span className="mt-1 font-mono text-[10px] text-indigo-400 h-4">{step >= 2 ? '1.2 GB/s Stream' : ''}</span>
          </div>

          <div className={`flex flex-col items-center transition-all duration-500 ${step >= 3 ? 'opacity-100 scale-110' : 'opacity-50'}`}>
            <div className={`w-16 h-16 rounded-xl flex items-center justify-center bg-[#1A1D23]/80 backdrop-blur-md border-2 transition-all ${step >= 3 ? 'border-rose-500 shadow-[0_0_30px_rgba(244,63,94,0.5)]' : 'border-[#2D3139]'}`}>
              <Zap className={`w-8 h-8 ${step >= 3 ? 'text-rose-500' : 'text-slate-500'}`} />
            </div>
            <span className="mt-4 font-mono text-xs text-rose-500 font-bold drop-shadow-[0_0_8px_#f43f5e]">PYTHON ML</span>
            <span className="mt-1 font-mono text-[10px] text-rose-400 h-4">{step >= 3 ? 'FastAPI Engaged' : ''}</span>
          </div>
        </div>
      </div>

    </div>
  );
};

export default ProcessingPage;