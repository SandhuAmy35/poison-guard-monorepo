import zmq
import json
import time
import random
import uuid

context = zmq.Context()
socket = context.socket(zmq.PUSH)
socket.connect("tcp://127.0.0.1:5555")

counter = 0
print("Starting C++ Stream Simulator (Strict API Contract)...")

while True:
    # Toggle between safe and poisoned data for the demo
    if counter % 2 == 0:
        risk = 0.1
        threats = 0
        print("🟢 Sent CLEAN batch to ZeroMQ...")
    else:
        risk = 0.99
        threats = 3
        print("🔴 Sent POISONED batch to ZeroMQ...")

    # --- EXACT MATCH: ZeroMQ Payload (C++ Core -> Python FastAPI) ---
    payload = {
        "batch_id": str(uuid.uuid4()),
        "timestamp": int(time.time()),
        "data_points": 5000,
        "flagged_indices": [102, 455, 1209] if risk > 0.8 else [],
        "layer1_metrics": {
            "avg_z_score": round(random.uniform(1.2, 2.8), 2),
            "iqr_outliers": random.randint(5, 15)
        },
        "raw_payload_base64": "ZHVtbXkgZGF0YQ==",
        
        # We append our hidden math vector so your PyTorch lie detector works!
        "demo_vector": [0.1, 0.2, risk],
        "ingestion_rate": f"{random.uniform(1.0, 1.5):.1f}GB/s",
        "active_threats": threats
    }
    
    socket.send_string(json.dumps(payload))
    counter += 1
    time.sleep(2)