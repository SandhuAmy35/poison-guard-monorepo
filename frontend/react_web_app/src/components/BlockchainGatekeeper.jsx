import React from 'react';
import { Hexagon, Fingerprint, Link, ShieldCheck, ExternalLink } from 'lucide-react';

const BlockchainGatekeeper = ({ step }) => {
  return (
    <div className="w-full py-2 relative">
      <div className="flex flex-col md:flex-row justify-between items-center w-full mx-auto gap-4 md:gap-0">
        
        {/* Step 1: Hashing */}
        <div className="flex flex-col items-center w-1/3 relative z-10">
          <div className="relative flex items-center justify-center w-14 h-14 mb-3">
            <Hexagon className={`absolute w-full h-full transition-colors duration-500 ${step >= 1 ? (step > 1 ? 'text-[#34C759]' : 'text-[#00E5FF] drop-shadow-[0_0_12px_rgba(0,229,255,0.5)]') : 'text-[#666666]'}`} strokeWidth={1} />
            <Fingerprint className={`w-5 h-5 transition-colors duration-500 ${step === 1 ? 'animate-pulse text-[#00E5FF]' : (step > 1 ? 'text-[#34C759]' : 'text-[#666666]')}`} />
          </div>
          <span className={`font-mono text-[10px] sm:text-xs tracking-widest font-bold uppercase transition-colors duration-500 ${step >= 1 ? 'text-slate-100' : 'text-[#666666]'}`}>SHA-256 Hashing</span>
          <div className={`mt-2 text-[10px] font-mono text-center transition-all duration-500 ${step >= 1 ? 'opacity-100' : 'opacity-0'}`}>
            <span className="text-slate-500 hidden lg:inline">UPI_Dataset.csv ➔ </span>
            <span className={step > 1 ? 'text-[#34C759]' : 'text-[#00E5FF]'}>0x4f...a9b</span>
          </div>
        </div>

        {/* Connector 1 */}
        <div className="hidden md:block absolute top-7 left-[20%] w-[26%] h-[2px] bg-[#2D3139] -z-10">
          <div className={`h-full w-full transition-opacity duration-500 ${step === 2 ? 'opacity-100 animate-data-flow' : (step > 2 ? 'bg-[#34C759]' : 'opacity-0')}`} />
        </div>

        {/* Step 2: Ledger Sync */}
        <div className="flex flex-col items-center w-1/3 relative z-10">
          <div className="relative flex items-center justify-center w-14 h-14 mb-3">
            <Hexagon className={`absolute w-full h-full transition-colors duration-500 ${step >= 2 ? (step > 2 ? 'text-[#34C759]' : 'text-[#00E5FF] drop-shadow-[0_0_12px_rgba(0,229,255,0.5)]') : 'text-[#666666]'}`} strokeWidth={1} />
            <Link className={`w-5 h-5 transition-all duration-500 ${step === 2 ? 'animate-spin-slow text-[#00E5FF]' : (step > 2 ? 'text-[#34C759]' : 'text-[#666666]')}`} />
          </div>
          <span className={`font-mono text-[10px] sm:text-xs tracking-widest font-bold uppercase transition-colors duration-500 ${step >= 2 ? 'text-slate-100' : 'text-[#666666]'}`}>Ledger Sync</span>
          <div className={`mt-2 text-[10px] font-mono text-center transition-all duration-500 ${step >= 2 ? 'opacity-100' : 'opacity-0'}`}>
            <span className="text-slate-400">Chain: <span className="text-[#00E5FF]">Polygon (Amoy)</span></span><br/>
            <span className="text-slate-500">Block: 104239</span>
          </div>
        </div>

        {/* Connector 2 */}
        <div className="hidden md:block absolute top-7 left-[54%] w-[26%] h-[2px] bg-[#2D3139] -z-10">
          <div className={`h-full w-full transition-opacity duration-500 ${step === 3 ? 'opacity-100 animate-data-flow' : (step > 3 ? 'bg-[#34C759]' : 'opacity-0')}`} />
        </div>

        {/* Step 3: Verified */}
        <div className="flex flex-col items-center w-1/3 relative z-10">
          <div className="relative flex items-center justify-center w-14 h-14 mb-3">
            <Hexagon className={`absolute w-full h-full transition-colors duration-500 ${step >= 3 ? 'text-[#34C759] drop-shadow-[0_0_15px_rgba(52,199,89,0.5)]' : 'text-[#666666]'}`} strokeWidth={1} />
            <ShieldCheck className={`w-5 h-5 transition-colors duration-500 ${step >= 3 ? 'text-[#34C759]' : 'text-[#666666]'}`} />
          </div>
          <span className={`font-mono text-[10px] sm:text-xs tracking-widest font-bold uppercase transition-colors duration-500 ${step >= 3 ? 'text-[#34C759]' : 'text-[#666666]'}`}>Verified</span>
          <div className={`mt-2 flex flex-col items-center gap-1 text-[10px] font-mono text-center transition-all duration-500 ${step >= 3 ? 'opacity-100' : 'opacity-0'}`}>
            <span className="text-[#34C759]">Hash Confirmed</span>
            <button className="flex items-center gap-1 text-slate-400 hover:text-white border border-slate-700 hover:border-slate-500 bg-slate-800/50 px-2 py-1 rounded transition-colors mt-1">
              <ExternalLink className="w-3 h-3" /> Explorer
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BlockchainGatekeeper;