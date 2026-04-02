import sys
import asyncio
import json
import zmq
import zmq.asyncio
import pandas as pd
import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from typing import List, Optional
from contextlib import asynccontextmanager

# Local Imports
from ml_classes import PyTorchShadowModel, ARTDetector, RAGRegulatorySidecar, StatisticalFilter
from rl_warden import RLWarden 

# ==========================================
# 0. CONFIGURATION & DOMAIN SWITCH
# ==========================================
# Set this to "CREDIT" to run the Credit Score dataset, or "UPI" for Fraud
DOMAIN_MODE = "CREDIT" 

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# ==========================================
# 1. WEB DASHBOARD HTML
# ==========================================
html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>PoisonGuard: Multi-Domain Command Center</title>
    <style>
        body {{ font-family: 'Courier New', monospace; background-color: #0d1117; color: #00ff00; padding: 20px; line-height: 1.2; }}
        .header {{ border-bottom: 2px solid #00ff00; padding-bottom: 10px; margin-bottom: 20px; }}
        .log-entry {{ margin-bottom: 10px; padding: 15px; border-left: 3px solid #30363d; background: #161b22; border-radius: 4px; }}
        .alert {{ color: #ff3333; border-left: 5px solid #ff3333; background: #2d1111; animation: blink 0.8s infinite; }}
        @keyframes blink {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0.7; }} 100% {{ opacity: 1; }} }}
        .metric {{ color: cyan; font-weight: bold; }}
        .rag-report {{ color: #8b949e; font-style: italic; margin-top: 5px; border-top: 1px solid #30363d; padding-top: 5px; }}
        .domain-tag {{ background: #00ff00; color: #000; padding: 2px 8px; font-weight: bold; border-radius: 3px; float: right; }}
    </style>
</head>
<body>
    <div class="header">
        <span class="domain-tag">ACTIVE DOMAIN: {DOMAIN_MODE}</span>
        <h1>🛡️ PoisonGuard: Multi-Layer Autonomous Defense</h1>
        <div id="status" style="color: cyan;">AWAITING WEBSOCKET...</div>
    </div>
    <div id="messages"></div>

    <script>
        const messagesDiv = document.getElementById('messages');
        const statusDiv = document.getElementById('status');
        const ws = new WebSocket(`ws://${{window.location.host}}/ws/dashboard`);

        ws.onopen = () => {{ 
            statusDiv.innerHTML = "STATUS: LIVE - SCANNING {DOMAIN_MODE} MANIFOLD"; 
            messagesDiv.innerHTML = ""; 
        }};

        ws.onmessage = (event) => {{
            const payload = JSON.parse(event.data);
            const data = payload.data;
            const isAnom = data.active_threats > 0;
            const div = document.createElement('div');
            div.className = 'log-entry' + (isAnom ? ' alert' : '');
            
            div.innerHTML = `
                <strong>SOURCE: ${{payload.type}} | BATCH: ${{data.batch_id}}</strong><br>
                <span class="metric">RL REWARD: ${{data.rl_reward}}</span> | 
                <span class="metric">EPS: ${{data.rl_new_eps}}</span> | 
                <span class="metric">CUDA: 42%</span><br>
                <div class="rag-report">${{data.rag_explanation}}</div>
                <pre style="color: #58a6ff; font-size: 11px; margin-top: 5px;">Input Vector [Feat1, Feat2, Label]: ${{JSON.stringify(data.cluster_delta)}}</pre>
            `;
            
            if (isAnom) {{
                div.innerHTML = "<h2>🚨 {DOMAIN_MODE} ANOMALY DETECTED 🚨</h2>" + div.innerHTML;
            }}

            messagesDiv.insertBefore(div, messagesDiv.firstChild);
        }};
        
        ws.onclose = () => {{ statusDiv.innerHTML = "STATUS: DISCONNECTED"; }};
    </script>
</body>
</html>
"""

# ==========================================
# 2. COMPONENT SETUP
# ==========================================
shadow = PyTorchShadowModel()
detector = ARTDetector()
warden = RLWarden()
rag = RAGRegulatorySidecar()
stats_filter = StatisticalFilter()

current_audit_task: Optional[asyncio.Task] = None
is_auditing = False

@asynccontextmanager
async def lifespan(app: FastAPI):
    zmq_task = asyncio.create_task(zmq_ingestion_loop())
    yield
    zmq_task.cancel()

app = FastAPI(lifespan=lifespan)

class ConnectionManager:
    def __init__(self): self.active_connections = []
    async def connect(self, ws): await ws.accept(); self.active_connections.append(ws)
    def disconnect(self, ws): self.active_connections.remove(ws)
    async def broadcast(self, msg):
        for c in self.active_connections:
            try: await c.send_json(msg)
            except: pass

manager = ConnectionManager()

# ==========================================
# 3. CORE LOGIC & PIPELINES
# ==========================================

async def auto_csv_audit():
    global is_auditing
    if is_auditing: return
    
    is_auditing = True
    detector.activation_buffer.clear()
    
    # Switch dataset based on mode
    csv_path = r"D:\indore\poison-guard-monorepo-s\python_ml_backend\credit_test.csv" if DOMAIN_MODE == "CREDIT" else r"D:\indore\poison-guard-monorepo-s\python_ml_backend\poison_test.csv"
    
    await asyncio.sleep(1.0) 
    try:
        if os.path.exists(csv_path):
            print(f"[AUTO-AUDIT] Running Domain: {DOMAIN_MODE}")
            df = pd.read_csv(csv_path)
            for i, row in df.iterrows():
                payload = {
                    "batch_id": f"{DOMAIN_MODE}_TRX_{i}",
                    "demo_vector": [float(row['feat1']), float(row['feat2']), float(row['risk_score'])],
                    "profile": DOMAIN_MODE
                }
                await process_data(payload, "AUTO_FORENSICS")
                await asyncio.sleep(1.3)
        else:
            print(f"[ERROR] {csv_path} missing. Run prepare_data script first.")
    finally:
        is_auditing = False

async def process_data(payload, source):
    profile = payload.get("profile", "UPI")
    
    # 1. LAYER 1: Statistical Check
    f1, f2 = payload["demo_vector"][0], payload["demo_vector"][1]
    is_stat_anomaly, stats_reason = stats_filter.check_heuristics(f1, f2)

    # 2. LAYER 2 & 3: Neural & Spectral
    ext = shadow.extract_activations(payload["demo_vector"])
    is_p, svd_flag = detector.detect_poison(ext)
    
    # RL Warden Adjustment
    rl_feedback = warden.evaluate_action(is_p or is_stat_anomaly, ext["true_label"])
    detector.eps_threshold = rl_feedback["new_eps"]
    
    # 4. LAYER 4: Groq Contextual Auditor
    report = f"Integrity Verified. Metrics within {profile} norm."
    
    if is_p or is_stat_anomaly or svd_flag:
        report = await asyncio.to_thread(
            rag.explain_threat, 
            payload.get("batch_id", "CSV"), 
            ext["mse_score"], 
            payload["demo_vector"],
            stats_reason,
            svd_flag,
            profile=profile # Pass domain context to LLM
        )

    await manager.broadcast({
        "type": source,
        "data": {
            "batch_id": payload.get("batch_id"),
            "active_threats": 1 if (is_p or is_stat_anomaly or svd_flag) else 0,
            "rl_reward": rl_feedback["reward"],
            "rl_new_eps": rl_feedback["new_eps"],
            "rag_explanation": f"[{rl_feedback['action_log']}] {report}",
            "cluster_delta": payload["demo_vector"] 
        }
    })

async def zmq_ingestion_loop():
    ctx = zmq.asyncio.Context()
    sock = ctx.socket(zmq.PULL); sock.bind("tcp://127.0.0.1:5555")
    while True:
        try:
            msg = await sock.recv_string()
            data = json.loads(msg)
            # Default to UPI for external streams unless specified
            data.setdefault("profile", "UPI")
            await process_data(data, "ZMQ_STREAM")
        except: await asyncio.sleep(0.1)

# ==========================================
# 4. ENDPOINTS
# ==========================================

@app.get("/", response_class=HTMLResponse)
async def root(): return html_content

@app.websocket("/ws/dashboard")
async def websocket_endpoint(ws: WebSocket):
    global current_audit_task
    await manager.connect(ws)
    if current_audit_task and not current_audit_task.done():
        current_audit_task.cancel()
    current_audit_task = asyncio.create_task(auto_csv_audit())
    try:
        while True: await ws.receive_text() 
    except WebSocketDisconnect:
        manager.disconnect(ws)