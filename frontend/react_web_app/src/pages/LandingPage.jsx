import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronRight } from 'lucide-react';

const LandingPage = () => {
  const navigate = useNavigate();
  
  useEffect(() => { 
    setTimeout(() => { 
      document.querySelectorAll('.word-animate').forEach(word => { 
        if (word) word.style.animation = 'word-appear 0.8s ease-out forwards'; 
      }); 
    }, 100); 
  }, []);
  
  return (
    <div className="flex flex-col justify-center items-center px-6 py-20 min-h-screen">
      <div className="text-center mb-8">
        <h2 className="text-xs sm:text-sm font-mono font-light text-slate-300 uppercase tracking-[0.2em] opacity-80">
          <span className="word-animate" data-delay="0">AI PoisonGuard</span> <span className="word-animate" data-delay="300">Terminal</span>
        </h2>
        <div className="mt-4 w-12 sm:w-16 h-px bg-gradient-to-r from-transparent via-slate-300 to-transparent opacity-30 mx-auto"></div>
      </div>
      <div className="text-center max-w-5xl mx-auto relative mb-16">
        <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-extralight leading-tight tracking-tight text-slate-50 text-decoration-animate pb-4">
          <div className="mb-4">
            <span className="word-animate text-[#00E5FF]" data-delay="700">Isolate</span> <span className="word-animate" data-delay="850">the</span> <span className="word-animate text-rose-400" data-delay="1000">poison,</span>
          </div>
          <div className="text-xl sm:text-2xl md:text-3xl font-thin text-slate-300 leading-relaxed tracking-wide">
            <span className="word-animate" data-delay="1400">where</span> <span className="word-animate" data-delay="1550">anomalies</span> <span className="word-animate" data-delay="1700">break</span> <span className="word-animate" data-delay="1850">and</span> <span className="word-animate" data-delay="2000">data</span> <span className="word-animate text-cyan-200" data-delay="2150">clarity</span> <span className="word-animate" data-delay="2300">is</span> <span className="word-animate" data-delay="2450">restored.</span>
          </div>
        </h1>
      </div>
      <div className="text-center">
        <button onClick={() => navigate('/upload')} className="opacity-0 group px-8 py-3 bg-white/5 hover:bg-white/10 border border-white/10 text-white rounded transition-all flex items-center gap-3 backdrop-blur-sm mx-auto" style={{ animation: 'word-appear 1s ease-out forwards', animationDelay: '3s' }}>
          <span className="font-light tracking-widest text-sm uppercase">Initialize Pipeline</span><ChevronRight className="w-4 h-4 opacity-50 group-hover:translate-x-1 group-hover:opacity-100 transition-all" />
        </button>
      </div>
    </div>
  );
};

export default LandingPage;