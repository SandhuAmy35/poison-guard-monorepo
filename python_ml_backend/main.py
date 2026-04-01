import sys
import asyncio
import json
import zmq
import zmq.asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from typing import List
from contextlib import asynccontextmanager

# --- REAL ML LOGIC IMPORTS ---
from ml_classes import PyTorchShadowModel, ARTDetector, RAGRegulatorySidecar
from rl_warden import RLWarden  # Your new dedicated RL file

# ==========================================
# 0. THE WINDOWS ASYNCIO FIX
# ==========================================
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# ==========================================
# 1. WEB DASHBOARD HTML (The "Matrix" UI)
# ==========================================
html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>PoisonGuard Level 3 Dashboard</title>
    <style>
        body { font-family: 'Courier New', monospace; background-color: #0d1117; color: #00ff00; padding: 20px; line-height: 1.2; }
        .header { border-bottom: 2px solid #00ff00; padding-bottom: 10px; margin-bottom: 20px; }
        .log-entry { margin-bottom: 10px; padding: 15px; border-left: 3px solid #30363d; background: #161b22; border-radius: 4px; }
        .alert { color: #ff3333; border-left: 5px solid #ff3333; background: #2d1111; animation: blink 1s infinite; }
        @keyframes blink { 0% { opacity: 1; } 50% { opacity: 0.8; } 100% { opacity: 1; } }
        .metric { color: cyan; font-weight: bold; }
        .rag-report { color: #8b949e; font-style: italic; margin-top: 5px; border-top: 1px solid #30363d; padding-top: 5px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🛡️ PoisonGuard: ML Core Telemetry</h1>
        <div id="status" style="color: cyan;">CONNECTING TO WEBSOCKET...</div>
    </div>
    <div id="messages"></div>

    <script>
        const messagesDiv = document.getElementById('messages');
        const statusDiv = document.getElementById('status');
        
        const ws = new WebSocket(`ws://${window.location.host}/ws/dashboard`);

        ws.onopen = () => { statusDiv.innerHTML = "STATUS: ONLINE - DSDP COMPLIANCE ENGINE ACTIVE"; };
        ws.onclose = () => { statusDiv.innerHTML = "STATUS: OFFLINE"; statusDiv.style.color = "red"; };

        ws.onmessage = (event) => {
            const payload = JSON.parse(event.data);
            const data = payload.data;
            const isPoison = data.active_threats > 0;
            
            const div = document.createElement('div');
            div.className = 'log-entry' + (isPoison ? ' alert' : '');
            
            const timestamp = new Date().toLocaleTimeString();
            div.innerHTML = `
                <strong>[${timestamp}] BATCH: ${data.batch_id}</strong><br>
                <span class="metric">RL REWARD SCORE: ${data.rl_reward}</span> | 
                <span class="metric">INGESTION: ${data.ingestion_rate}</span><br>
                <div class="rag-report">${data.rag_explanation}</div>
                <pre style="color: #58a6ff;">Cluster Delta: ${JSON.stringify(data.cluster_delta)}</pre>
            `;
            
            if (isPoison) {
                div.innerHTML = "<h2>🚨 POISON CLUSTER ISOLATED 🚨</h2>" + div.innerHTML;
            }

            messagesDiv.insertBefore(div, messagesDiv.firstChild);
            if (messagesDiv.children.length > 20) messagesDiv.removeChild(messagesDiv.lastChild);
        };
    </script>
</body>
</html>
"""

# ==========================================
# 2. CORE COMPONENT INITIALIZATION
# ==========================================
shadow_model = PyTorchShadowModel()
art_detector = ARTDetector()
rl_warden = RLWarden()
rag_sidecar = RAGRegulatorySidecar()

# ==========================================
# 3. FASTAPI SETUP
# ==========================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(zmq_ingestion_loop())
    yield
    task.cancel()

app = FastAPI(title="PoisonGuard ML Core", lifespan=lifespan)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass

manager = ConnectionManager()

# ==========================================
# 4. ZEROMQ -> ML -> WEBSOCKET PIPELINE
# ==========================================
async def zmq_ingestion_loop():
    ctx = zmq.asyncio.Context()
    sock = ctx.socket(zmq.PULL)
    sock.bind("tcp://127.0.0.1:5555")
    
    print("[ZMQ] Listening for high-speed C++ ingestion stream...")

    while True:
        try:
            msg = await sock.recv_string()
            payload = json.loads(msg)
            
            # 1. Shadow Model Inference
            extract = shadow_model.extract_activations(payload["demo_vector"])
            
            # 2. DBSCAN Anomaly Detection
            is_poisoned = art_detector.detect_poison(extract)
            
            # 3. RL Policy Evaluation (The Warden)
            current_reward = rl_warden.evaluate_action(is_poisoned, extract["risk_score"])
            
            # 4. RAG Audit Report Generation
            report = "SYSTEM NOMINAL: Data stream verified clean."
            if is_poisoned:
                report = rag_sidecar.explain_threat(payload["batch_id"], extract["risk_score"])
            
            # 5. Broadcast to Dashboard
            ws_payload = {
                "type": "TELEMETRY_UPDATE",
                "data": {
                    "batch_id": payload.get("batch_id"),
                    "ingestion_rate": payload.get("ingestion_rate", "1.2GB/s"),
                    "active_threats": 1 if is_poisoned else 0,
                    "rl_reward": current_reward,
                    "rag_explanation": report,
                    "cluster_delta": [round(v, 2) for v in extract["activations"][:3]]
                }
            }
            await manager.broadcast(ws_payload)
            
        except Exception as e:
            print(f"[ERROR] Pipeline Failure: {e}")

# ==========================================
# 5. ENDPOINTS
# ==========================================

@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    return html_content

@app.websocket("/ws/dashboard")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text() 
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/health")
async def health_check():
    return {"status": "Active", "engine": "ZMQ-PyTorch-DBSCAN-RL-RAG"}