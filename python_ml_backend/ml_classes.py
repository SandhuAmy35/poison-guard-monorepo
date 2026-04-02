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

# ==========================================
# 0. MVP: Statistical Analysis (Z-Score & IQR)
# ==========================================
class StatisticalFilter:
    def __init__(self):
        print("[ML] Initializing Statistical Baseline (Z-Score + IQR)...")
        self.history_feat1 = []
        self.history_feat2 = []

    def check_heuristics(self, feat1, feat2):
        """Checks for basic statistical anomalies (Generic for UPI or Credit)."""
        self.history_feat1.append(feat1)
        self.history_feat2.append(feat2)
        
        if len(self.history_feat1) > 100:
            self.history_feat1.pop(0)
            self.history_feat2.pop(0)

        if len(self.history_feat1) < 10:
            return False, "Warmup"

        # 1. Z-Score Detection
        z_f1 = np.abs(stats.zscore(self.history_feat1)[-1])
        z_f2 = np.abs(stats.zscore(self.history_feat2)[-1])
        
        # 2. IQR (Interquartile Range) Detection
        q75, q25 = np.percentile(self.history_feat2, [75, 25])
        iqr = q75 - q25
        upper_bound = q75 + (1.5 * iqr)
        is_iqr_outlier = feat2 > upper_bound

        if z_f1 > 3.0 or z_f2 > 3.0:
            return True, "Z-Score Outlier"
        if is_iqr_outlier:
            return True, "IQR Manifold Anomaly"
            
        return False, "Clean"

# ==========================================
# 1. The Authentic Autoencoder
# ==========================================
class UPIAutoencoder(nn.Module):
    def __init__(self):
        super(UPIAutoencoder, self).__init__()
        # Manifold Compression: [Feat1, Feat2] -> [Latent] -> [Feat1, Feat2]
        self.encoder = nn.Sequential(
            nn.Linear(2, 4),
            nn.ReLU(),
            nn.Linear(4, 1) 
        )
        self.decoder = nn.Sequential(
            nn.Linear(1, 4),
            nn.ReLU(),
            nn.Linear(4, 2)
        )

    def forward(self, x):
        latent = self.encoder(x)
        reconstructed = self.decoder(latent)
        return reconstructed, latent

# ==========================================
# 2. PyTorch Shadow Model (Autoencoder Engine)
# ==========================================
class PyTorchShadowModel:
    def __init__(self):
        print("[ML] Initializing Neural Reconstruction Engine...")
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = UPIAutoencoder().to(self.device)
        self.model.eval() 

    def extract_activations(self, data_vector):
        tensor_data = torch.tensor(data_vector[:2], dtype=torch.float32).to(self.device).unsqueeze(0)
        
        with torch.no_grad():
            reconstructed, latent = self.model(tensor_data)
            
        mse_loss = torch.nn.functional.mse_loss(reconstructed, tensor_data).item()
        latent_list = latent.cpu().numpy().flatten().tolist()
        cluster_input = [latent_list[0], mse_loss]
        
        return {
            "activations": cluster_input, 
            "mse_score": mse_loss, 
            "true_label": data_vector[2]
        }

# ==========================================
# 3. Activation Clustering + Spectral SVD
# ==========================================
class ARTDetector:
    def __init__(self):
        print("[ML] Initializing Spectral Clustering (DBSCAN + SVD)...")
        self.activation_buffer = []
        self.batch_size = 5 
        self.eps_threshold = 0.15 

    def detect_poison(self, activations_dict):
        self.activation_buffer.append(activations_dict["activations"])
        
        is_poisoned = False
        svd_flag = False
        
        if len(self.activation_buffer) >= self.batch_size:
            svd_flag = self._run_spectral_svd()
            is_poisoned = self._run_clustering() or svd_flag
            self.activation_buffer.clear() 
            
        return is_poisoned, svd_flag

    def _run_spectral_svd(self):
        try:
            X = np.array(self.activation_buffer)
            U, S, V = np.linalg.svd(X)
            spectral_signature = S[0] / (np.sum(S) + 1e-9)
            return spectral_signature > 0.95 
        except:
            return False

    def _run_clustering(self):
        X = np.array(self.activation_buffer)
        clustering = DBSCAN(eps=self.eps_threshold, min_samples=2).fit(X)
        return -1 in set(clustering.labels_) or len(set(clustering.labels_)) > 1

# ==========================================
# 4. Multi-Domain Automated Auditor (Cloud RAG)
# ==========================================
class RAGRegulatorySidecar:
    def __init__(self):
        print("[ML] Initializing Multi-Domain Cloud Auditor...")
        
        self.client = None
        self.model_name = "llama-3.1-8b-instant"

        if GROQ_AVAILABLE:
            try:
                self.client = Groq(api_key=self.api_key)
            except Exception as e:
                print(f"[ML] Groq Init Error: {e}")
        else:
            print("[ML] Groq SDK Missing.")

    def explain_threat(self, batch_id, risk_score, raw_vector, stats_reason, svd_flag, profile="UPI"):
        # Layer 1: Context Switching
        if profile == "CREDIT":
            # Feature mapping for Credit Dataset
            income = round(raw_vector[0] * 100, 2)
            debt_ratio = round(raw_vector[1] * 20, 2) # Inverse of our normalization
            domain_context = f"Income Percentile: {income}%, Debt/Income Ratio: {debt_ratio}"
            task_instruction = "Write a strict credit denial report focusing on Debt-to-Income insolvency."
        else:
            # Feature mapping for UPI/Fraud Dataset
            amount = round(raw_vector[0] * 1000.0, 2)
            distance = round(raw_vector[1] * 100.0, 2)
            domain_context = f"Amount: ₹{amount}, Origin Distance: {distance}km from Home Zone"
            task_instruction = "Write a professional fraud isolation report focusing on Geospatial Latent Deviation or Impossible Travel."

        svd_status = "Spectral Structural Anomaly Detected." if svd_flag else "Spectral Normal."

        # Layer 2: Unified Prompting
        prompt = f"""
        [SYSTEM: MULTI-DOMAIN COMPLIANCE AUDIT | PROFILE: {profile}]
        Entity ID: {batch_id}
        Metrics: {domain_context}
        Heuristics: {stats_reason}
        Spectral: {svd_status}
        Autoencoder MSE: {round(risk_score, 4)}
        
        Task: {task_instruction}
        Constraints: Professional 1-sentence response. NO pleasantries. Output ONLY the sentence.
        """

        if self.client is None:
            return f"AUDIT {batch_id}: Anomaly detected ({profile} Mode). MSE: {round(risk_score,4)}"

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model_name,
                temperature=0.1,
                max_tokens=100
            )
            return chat_completion.choices[0].message.content.strip()
        except Exception as e:
            print(f"[LLM ERROR] {e}")
            return f"FORENSIC ALERT {batch_id}: Neural deviation {round(risk_score, 4)} triggers {profile} isolation."