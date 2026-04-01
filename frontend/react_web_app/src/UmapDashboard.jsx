import React, { useState, useEffect } from 'react';
import DeckGL from '@deck.gl/react';
import { ScatterplotLayer } from '@deck.gl/layers';

const INITIAL_VIEW_STATE = {
  longitude: 0,
  latitude: 0,
  zoom: 4,
  maxZoom: 16,
  pitch: 0,
  bearing: 0
};

// Helper to generate 5,000 mock datasets
function generateMockData(isPoisonedState) {
  const points = [];
  const totalNodes = 5000;
  const poisonedCount = 150; 

  for (let i = 0; i < totalNodes; i++) {
    const isPoisonTarget = i < poisonedCount;
    let x = (Math.random() - 0.5) * 15;
    let y = (Math.random() - 0.5) * 15;
    let is_poisoned = false;
    let risk_score = Math.random() * 0.2;

    if (isPoisonTarget && isPoisonedState) {
      x = 12 + (Math.random() - 0.5) * 3; 
      y = 12 + (Math.random() - 0.5) * 3;
      is_poisoned = true;
      risk_score = 0.8 + Math.random() * 0.2;
    }

    points.push({
      id: `txn_UPI_${10000 + i}`,
      x,
      y,
      is_poisoned,
      risk_score: risk_score.toFixed(2)
    });
  }
  return points;
}

export default function UmapDashboard() {
  const [data, setData] = useState([]);
  const [status, setStatus] = useState("SYSTEM READY // AWAITING INGESTION");
  const [isAttacked, setIsAttacked] = useState(false);

  useEffect(() => {
    setData(generateMockData(false));
  }, []);

  const triggerAttack = () => {
    setStatus("CRITICAL: ADVERSARIAL SHIFT DETECTED IN CLUSTER-4");
    setIsAttacked(true);
    setData(generateMockData(true));
  };
  
  const resetSystem = () => {
    setStatus("SYSTEM READY // AWAITING INGESTION");
    setIsAttacked(false);
    setData(generateMockData(false));
  };

  const layer = new ScatterplotLayer({
    id: 'umap-cluster-layer',
    data,
    pickable: true,
    opacity: 0.8,
    stroked: true,
    filled: true,
    radiusScale: 6,
    radiusMinPixels: 2,
    radiusMaxPixels: 6,
    lineWidthMinPixels: 1,
    getPosition: d => [d.x, d.y],
    transitions: {
      getPosition: { duration: 1800, easing: t => t * (2 - t) },
      getFillColor: { duration: 500 }
    },
    getFillColor: d => d.is_poisoned ? [255, 50, 50, 255] : [0, 200, 255, 80],
    getLineColor: d => d.is_poisoned ? [255, 0, 0] : [0, 100, 150],
  });

  return (
    <div style={{ width: '100vw', height: '100vh', backgroundColor: '#050505' }}>
      <div style={{ position: 'absolute', top: 20, left: 20, zIndex: 10, color: '#00ffff', fontFamily: 'monospace' }}>
        <h1 style={{ margin: 0, fontSize: '24px', textShadow: '0 0 10px #00ffff', fontWeight: 'bold' }}>AI POISONGUARD</h1>
        <h2 style={{ margin: '5px 0', fontSize: '14px', color: isAttacked ? '#ff3333' : '#00ffff', letterSpacing: '1px' }}>
          {status}
        </h2>
        <div style={{ marginTop: '20px', fontSize: '12px', opacity: 0.8 }}>
          <p>DOMAIN: UPI FRAUD DETECTION PROFILE</p>
          <p>ACTIVE NODES: {data.length.toLocaleString()}</p>
        </div>
        
        <div style={{ marginTop: '30px', display: 'flex', gap: '10px' }}>
            <button onClick={triggerAttack} style={{ background: '#ff3333', color: 'black', border: 'none', padding: '8px 15px', fontWeight: 'bold', cursor: 'pointer', fontFamily: 'monospace' }}>
              [ SIMULATE POISONING ]
            </button>
            <button onClick={resetSystem} style={{ background: 'transparent', color: '#00ffff', border: '1px solid #00ffff', padding: '8px 15px', cursor: 'pointer', fontFamily: 'monospace' }}>
              HEAL
            </button>
        </div>
      </div>
      <DeckGL
        initialViewState={INITIAL_VIEW_STATE}
        controller={true}
        layers={[layer]}
        getTooltip={({object}) => object && `Txn ID: ${object.id}\nRisk Score: ${object.risk_score}`}
      />
    </div>
  );
}