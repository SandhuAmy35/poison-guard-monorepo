# 🛡️ PoisonGuard
**High-Performance, Hardware-Accelerated Threat Isolation Pipeline**

[![C++17](https://img.shields.io/badge/C++-17-blue.svg)](https://isocpp.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-CUDA_Accelerated-EE4C2C.svg)](https://pytorch.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-Vite-61DAFB.svg)](https://reactjs.org/)
[![ZeroMQ](https://img.shields.io/badge/ZeroMQ-IPC_Stream-red.svg)](https://zeromq.org/)

PoisonGuard is a distributed, high-throughput fraud detection microservice architecture. It bridges bare-metal memory mapping, reinforcement-learning-tuned anomaly detection, and real-time WebGL visualization to isolate financial threats at over 1,500 transactions per second.

---

## 🧠 System Architecture

Unlike traditional monolithic machine learning pipelines, PoisonGuard decouples ingestion, inference, and UI across a hyper-fast ZeroMQ IPC bridge:

1. **Bare-Metal Ingestion Core (C++17):** Bypasses standard I/O bottlenecks using `mmap` for zero-copy memory loading. It computes a cryptographic SHA-256 provenance hash via OpenSSL before streaming data at raw NVMe speeds.
2. **PyTorch Shadow Model & RL Warden (Python):** A hardware-accelerated Autoencoder running on NVIDIA RTX VRAM. A custom Reinforcement Learning (RL) Warden dynamically tunes the DBSCAN clustering epsilon to minimize the False Positive Rate (FPR) in real-time.
3. **RAG Regulatory Sidecar (LLaMA-3.1 via Groq):** Employs asynchronous micro-batching to generate human-readable, forensic audit logs for flagged transactions without blocking the high-speed ingestion stream.
4. **Hacker TUI & React Dashboard:** Dual interfaces. A Textual-based Python terminal UI tracks raw CUDA metrics and RL rewards, while a React/Recharts WebGL dashboard plots the latent vectors dynamically.

---

## ⚙️ Prerequisites

To run this pipeline locally, your machine requires:
* **C++ Build Tools:** `g++`, `make`
* **Libraries:** `libzmq3-dev` (ZeroMQ), `libssl-dev` (OpenSSL)
* **Python:** 3.10+ with `pip`
* **Node.js:** v18+ with `npm`
* *(Optional but recommended)* **NVIDIA GPU** with CUDA toolkit installed.

---

## 🚀 Manual Launch Sequence

To run the architecture natively (without Docker), you must spin up the components individually in separate terminal sessions.

### Step 1: Install Python Dependencies
```bash
cd python_ml_backend
pip install fastapi uvicorn websockets pyzmq torch scikit-learn scipy numpy groq pynvml textual
```

### Step 2: Boot the AI Backend (Terminal 1)
```bash
cd python_ml_backend
export GROQ_API_KEY="your_groq_api_key_here"
export CUDA_VISIBLE_DEVICES=0 
python main.py
```

Step 3: Launch the Hacker TUI (Terminal 2)
```bash
cd python_ml_backend
python tui_dashboard.py
```

Step 4: Boot the React Dashboard (Terminal 3)
```bash
cd python_ml_backend
python tui_dashboard.py
```

Step 5: Fire the C++ Core (Terminal 4)
```bash
cd cpp_ingestion_core
g++ src/main.cpp src/zmq_client.cpp -o ingestion_core -I./src -lzmq -lcrypto -lssl

# Execute the binary and pass the dataset and domain profile (UPI or CREDIT)
./ingestion_core ../shared_data/example_data Profile
```




