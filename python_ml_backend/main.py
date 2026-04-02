import sys
import asyncio
import json
import zmq
import zmq.asyncio
import time
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager

from ml_classes import PyTorchShadowModel, ARTDetector, RAGRegulatorySidecar, StatisticalFilter
from rl_warden import RLWarden

if sys.platform == 'win32': asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

shadow_model = PyTorchShadowModel()
art_detector = ARTDetector()
rl_warden = RLWarden()
rag_sidecar = RAGRegulatorySidecar()
stats_filter = StatisticalFilter()

# THE FIX: Global cache so the ingestion loop never waits for the internet
global_rag_cache = "Awaiting initial threat signature..."

async def fetch_rag_background(batch_id, mse, vec, reason, svd, profile):
    global global_rag_cache
    try:
        # This happens silently in the background now!
        rep = await asyncio.to_thread(rag_sidecar.explain_threat, batch_id, mse, vec, reason, svd, profile)
        global_rag_cache = rep
    except Exception:
        pass

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(zmq_ingestion_loop())
    yield
    task.cancel()

app = FastAPI(title="PoisonGuard", lifespan=lifespan)

# --- CORS ALLOWANCE FOR REACT VITE FRONTEND ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>PoisonGuard: Web Command Center</title>
    <style>
        body { font-family: 'Courier New', monospace; background-color: #0d1117; color: #00ff00; padding: 20px; line-height: 1.2; }
        .log-entry { margin-bottom: 10px; padding: 15px; border-left: 3px solid #30363d; background: #161b22; }
        .alert { color: #ff3333; border-left: 5px solid #ff3333; background: #2d1111; }
        .rag-report { color: #8b949e; font-style: italic; margin-top: 5px; border-top: 1px solid #30363d; padding-top: 5px; }
    </style>
</head>
<body>
    <h1>🛡️ PoisonGuard: RAG Audit Log</h1>
    <div id="messages"></div>
    <script>
        const messagesDiv = document.getElementById('messages');
        const ws = new WebSocket(`ws://${window.location.host}/ws/dashboard`);
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data).data;
            const isPoison = data.active_threats > 0;
            const div = document.createElement('div');
            div.className = 'log-entry' + (isPoison ? ' alert' : '');
            div.innerHTML = `
                <strong>BATCH: ${data.batch_id}</strong> | REWARD: ${data.rl_reward}
                <div class="rag-report">${data.rag_explanation}</div>
            `;
            messagesDiv.insertBefore(div, messagesDiv.firstChild);
            if (messagesDiv.children.length > 20) messagesDiv.removeChild(messagesDiv.lastChild);
        };
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    return html_content

@app.post("/api/ingest")
async def ingest_data(domain: str = Form(...), dataset: UploadFile = File(None), model: UploadFile = File(None)):
    return {"status": "success", "domain": domain, "message": "Sequence Initiated"}


class ConnectionManager:
    def __init__(self): self.active_connections = []
    async def connect(self, ws: WebSocket): await ws.accept(); self.active_connections.append(ws)
    def disconnect(self, ws: WebSocket): self.active_connections.remove(ws)
    async def broadcast(self, msg: dict):
        for c in self.active_connections:
            try: await c.send_json(msg)
            except: pass

manager = ConnectionManager()

# Add this right above the loop
global_rag_cache = "Awaiting initial threat signature..."
global_cm = {"TP": 0, "TN": 0, "FP": 0, "FN": 0} # NEW: Global Confusion Matrix

async def zmq_ingestion_loop():
    global global_rag_cache, global_cm
    ctx = zmq.asyncio.Context()
    sock = ctx.socket(zmq.PULL)
    sock.bind("tcp://0.0.0.0:5555")
    print("[SYSTEM] ZMQ Listening on 5555")
    
    last_groq_call = 0.0

    while True:
        try:
            msg = await sock.recv_string()
            clean_msg = msg.replace("nan", "0.0").replace("inf", "0.0").replace("-inf", "0.0").replace("NaN", "0.0")
            payload = json.loads(clean_msg)
            vector = payload["demo_vector"]
            profile = payload.get("profile", "UPI")

            is_stat_anomaly, stats_reason = stats_filter.check_heuristics(vector[0], vector[1])
            ext = shadow_model.extract_activations(vector)
            is_poisoned, svd_flag = art_detector.detect_poison(ext)
            
            is_threat = is_poisoned or is_stat_anomaly or svd_flag
            rl_feed = rl_warden.evaluate_action(is_threat, ext["true_label"])
            art_detector.eps_threshold = rl_feed["new_eps"]
            
            # --- NEW: UPDATE CONFUSION MATRIX ---
            is_actual_poison = (ext["true_label"] == 1)
            if is_threat and is_actual_poison: global_cm["TP"] += 1
            elif is_threat and not is_actual_poison: global_cm["FP"] += 1
            elif not is_threat and not is_actual_poison: global_cm["TN"] += 1
            elif not is_threat and is_actual_poison: global_cm["FN"] += 1

            if is_threat:
                now = time.time()
                if now - last_groq_call > 3.0 and rag_sidecar.client is not None:
                    last_groq_call = now
                    asyncio.create_task(fetch_rag_background(payload["batch_id"], ext["mse_score"], vector, stats_reason, svd_flag, profile))
                report = f"MSE: {round(ext['mse_score'], 4)} | AUDIT: {global_rag_cache}"
            else:
                report = "Integrity Verified. Transaction nominal."

            await manager.broadcast({
                "type": "TELEMETRY_UPDATE",
                "data": {
                    "batch_id": payload["batch_id"],
                    "active_threats": 1 if is_threat else 0,
                    "rl_reward": rl_feed["reward"],
                    "rl_new_eps": rl_feed["new_eps"],
                    "rag_explanation": f"[{rl_feed['action_log']}] {report}",
                    "cluster_delta": [round(v, 4) for v in vector],
                    "metrics": global_cm  # NEW: Send metrics to the UI
                }
            })
        except Exception as e:
            print(f"[ERROR] {e}")
            await asyncio.sleep(0.1)
            
@app.websocket("/ws/dashboard")
async def websocket_endpoint(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True: await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(ws)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="info")
