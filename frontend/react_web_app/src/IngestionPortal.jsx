import React, { useState } from 'react';

export default function IngestionPortal({ onStartScan }) {
  const [file, setFile] = useState(null);
  const [isVerifying, setIsVerifying] = useState(false);

  const styles = {
    container: {
      minHeight: '100vh',
      backgroundColor: '#050505',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      fontFamily: 'monospace',
      color: '#00ffff'
    },
    card: {
      width: '450px',
      backgroundColor: '#0a0a0a',
      border: '1px solid #003333',
      padding: '40px',
      borderRadius: '4px',
      boxShadow: '0 0 20px rgba(0, 255, 255, 0.05)',
      position: 'relative',
      textAlign: 'center'
    },
    title: { fontSize: '22px', fontWeight: 'bold', margin: '0 0 10px 0', color: '#00ffff', letterSpacing: '2px' },
    subtitle: { fontSize: '10px', color: '#006666', marginBottom: '30px', letterSpacing: '1px' },
    domainBox: {
      backgroundColor: '#001111',
      border: '1px solid #004444',
      color: '#00ffff',
      padding: '12px',
      fontSize: '12px',
      marginBottom: '20px',
      textTransform: 'uppercase',
      textAlign: 'left'
    },
    dropzone: {
      border: '1px dashed #004444',
      padding: '30px 10px',
      borderRadius: '4px',
      cursor: 'pointer',
      marginBottom: '20px',
      color: file ? '#ffffff' : '#006666',
      transition: '0.3s'
    },
    buttonMain: {
      width: '100%',
      padding: '16px',
      backgroundColor: isVerifying ? '#111' : '#00ffff',
      color: '#000',
      border: 'none',
      fontWeight: '900',
      cursor: 'pointer',
      textTransform: 'uppercase',
      letterSpacing: '2px',
      marginBottom: '10px'
    },
    buttonDemo: {
      width: '100%',
      padding: '10px',
      backgroundColor: 'transparent',
      color: '#008888',
      border: '1px solid #004444',
      fontSize: '10px',
      cursor: 'pointer',
      textTransform: 'uppercase',
      letterSpacing: '1px'
    }
  };

  const handleUpload = () => {
    if (!file) return alert("CRITICAL: NO_FILE_DETECTED.");
    setIsVerifying(true);
    setTimeout(() => {
      setIsVerifying(false);
      onStartScan(file, "UPI_FRAUD_ANALYSIS");
    }, 2000);
  };

  // The "Quick Demo" bypass
  const handleDemoBypass = () => {
    onStartScan({ name: "DEMO_DATASET.csv" }, "UPI_FRAUD_DEMO");
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <div style={{position: 'absolute', top: 0, left: 0, width: '100%', height: '2px', backgroundColor: '#00ffff'}} />
        
        <h1 style={styles.title}>POISONGUARD</h1>
        <p style={styles.subtitle}>SECURE GATEWAY // LAYER 0 PROVENANCE</p>

        <div style={styles.domainBox}>
          <span style={{fontSize: '8px', color: '#006666'}}>ACTIVE DOMAIN:</span><br/>
          &gt; UPI TRANSACTION ANALYSIS
        </div>

        <div style={styles.dropzone} onClick={() => document.getElementById('fp').click()}>
          <input type="file" id="fp" hidden onChange={(e) => setFile(e.target.files[0])} accept=".csv" />
          <div style={{fontSize: '24px', marginBottom: '5px'}}>{file ? '⚡' : '📂'}</div>
          <div style={{fontSize: '10px'}}>{file ? file.name : "SELECT DATASET (.CSV)"}</div>
        </div>

        <button style={styles.buttonMain} onClick={handleUpload} disabled={isVerifying}>
          {isVerifying ? "HASHING..." : "INITIALIZE SCAN"}
        </button>

        <button 
          style={styles.buttonDemo} 
          onClick={handleDemoBypass}
          onMouseOver={(e) => {e.target.style.color='#00ffff'; e.target.style.borderColor='#00ffff'}}
          onMouseOut={(e) => {e.target.style.color='#008888'; e.target.style.borderColor='#004444'}}
        >
          [ BYPASS TO DEMO VIEW ]
        </button>

        <div style={{marginTop: '25px', fontSize: '8px', color: '#003333'}}>
          ZMQ_STATUS: ONLINE | NODE: 0x71C...
        </div>
      </div>
    </div>
  );
}