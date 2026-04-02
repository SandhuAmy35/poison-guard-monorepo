import os
import torch
import torch.nn as nn
import numpy as np
from scipy import stats
from sklearn.cluster import DBSCAN

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    Groq = None
    GROQ_AVAILABLE = False

class StatisticalFilter:
    def __init__(self):
        self.history_feat1, self.history_feat2 = [], []

    def check_heuristics(self, feat1, feat2):
        self.history_feat1.append(feat1); self.history_feat2.append(feat2)
        if len(self.history_feat1) > 100: 
            self.history_feat1.pop(0); self.history_feat2.pop(0)
        if len(self.history_feat1) < 15: # Increased warmup for better stats
            return False, "Warmup"

        z_f1 = np.abs(stats.zscore(self.history_feat1)[-1])
        z_f2 = np.abs(stats.zscore(self.history_feat2)[-1])
        q75, q25 = np.percentile(self.history_feat2, [75, 25])
        
        # FIX: Increased IQR multiplier from 1.5 to 3.5 (Extreme Outlier detection)
        is_iqr_outlier = feat2 > (q75 + (3.5 * (q75 - q25)))

        # FIX: Increased Z-Score limit from 3.0 to 5.0 
        if z_f1 > 5.0 or z_f2 > 5.0: return True, "Extreme Z-Score Outlier"
        if is_iqr_outlier: return True, "Manifold Deviation"
        return False, "Clean"

class UPIAutoencoder(nn.Module):
    def __init__(self):
        super().__init__()
        self.encoder = nn.Sequential(nn.Linear(2, 4), nn.ReLU(), nn.Linear(4, 1))
        self.decoder = nn.Sequential(nn.Linear(1, 4), nn.ReLU(), nn.Linear(4, 2))
    def forward(self, x):
        latent = self.encoder(x)
        return self.decoder(latent), latent

class PyTorchShadowModel:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = UPIAutoencoder().to(self.device)
        self.model.eval() 

    def extract_activations(self, data_vector):
        tensor_data = torch.tensor(data_vector[:2], dtype=torch.float32).to(self.device).unsqueeze(0)
        with torch.no_grad():
            reconstructed, latent = self.model(tensor_data)
        mse_loss = torch.nn.functional.mse_loss(reconstructed, tensor_data).item()
        return {"activations": [latent.cpu().numpy().flatten()[0], mse_loss], "mse_score": mse_loss, "true_label": data_vector[2]}

class ARTDetector:
    def __init__(self):
        self.activation_buffer = []
        self.eps_threshold = 0.5 

    def detect_poison(self, activations_dict):
        self.activation_buffer.append(activations_dict["activations"])
        is_poisoned, svd_flag = False, False
        
        # THE FIX: Increased cluster buffer from 20 to 50 for more context
        if len(self.activation_buffer) >= 50:
            try:
                X = np.array(self.activation_buffer)
                U, S, V = np.linalg.svd(X)
                svd_flag = (S[0] / (np.sum(S) + 1e-9)) > 0.95 
            except: pass
            clustering = DBSCAN(eps=self.eps_threshold, min_samples=2).fit(np.array(self.activation_buffer))
            is_poisoned = -1 in set(clustering.labels_) or len(set(clustering.labels_)) > 1
            self.activation_buffer.clear() 
        return is_poisoned or svd_flag, svd_flag

class RAGRegulatorySidecar:
    def __init__(self):
        self.client = None
        self.model_name = "llama-3.1-8b-instant"
        # REPLACE THIS KEY WITH A VALID ONE IF YOU WANT REAL RAG LATER
       
        if GROQ_AVAILABLE and self.api_key:
            try: 
                self.client = Groq(api_key=self.api_key)
            except: 
                self.client = None

    def explain_threat(self, batch_id, risk_score, raw_vector, stats_reason, svd_flag, profile="UPI"):
        # Layer 1: Domain Mapping
        if profile == "CREDIT":
            ctx = f"Income: {round(raw_vector[0]*100,2)}%, Debt: {round(raw_vector[1]*20,2)}"
            task = "Write a strict credit denial report focusing on Debt-to-Income insolvency."
        else:
            ctx = f"Amount: ₹{round(raw_vector[0]*1000.0,2)}, Dist: {round(raw_vector[1]*100.0,2)}km"
            task = "Write a professional fraud isolation report focusing on Geospatial Latent Deviation."

        # PRIMARY FALLBACK: Includes MSE so each flag looks unique on the TUI
        if self.client is None:
            return f"FORENSIC ALERT {batch_id}: Neural deviation detected. (Audit Pending) | Latent MSE: {round(risk_score, 6)}"

        try:
            res = self.client.chat.completions.create(
                messages=[{"role": "user", "content": f"[SYSTEM: {profile}]\nID: {batch_id}\nMetrics: {ctx}\nTask: {task}\nConstraints: 1 sentence. Professional."}],
                model=self.model_name, temperature=0.1, max_tokens=100
            )
            return res.choices[0].message.content.strip()
        except Exception as e:
            # SECONDARY FALLBACK: Triggered on API errors (like 401 Invalid Key)
            return f"FORENSIC ALERT {batch_id}: Neural deviation detected. (Audit Pending) | Latent MSE: {round(risk_score, 6)}"
