import React, { useState, useEffect, memo } from 'react';

const InteractiveBackground = memo(() => {
  const [mouse, setMouse] = useState({ left: '0px', top: '0px', opacity: 0 });

  useEffect(() => {
    const handleMouseMove = (e) => setMouse({ left: `${e.clientX}px`, top: `${e.clientY}px`, opacity: 1 });
    const handleMouseLeave = () => setMouse(prev => ({ ...prev, opacity: 0 }));
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseleave', handleMouseLeave);
    return () => { 
      document.removeEventListener('mousemove', handleMouseMove); 
      document.removeEventListener('mouseleave', handleMouseLeave); 
    };
  }, []);

  return (
    <div className="fixed inset-0 pointer-events-none z-0 bg-gradient-to-br from-[#1A1D23] via-black to-[#111317]">
      <svg className="absolute inset-0 w-full h-full opacity-30" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <pattern id="gridPattern" width="60" height="60" patternUnits="userSpaceOnUse">
            <path d="M 60 0 L 0 0 0 60" fill="none" stroke="rgba(100, 116, 139, 0.2)" strokeWidth="1"/>
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#gridPattern)" />
      </svg>
      <div className="absolute w-96 h-96 blur-3xl rounded-full bg-[#00E5FF]/10 transition-opacity duration-500" 
           style={{ left: mouse.left, top: mouse.top, opacity: mouse.opacity, transform: 'translate(-50%, -50%)' }} />
    </div>
  );
});

export default InteractiveBackground;