import pandas as pd
import numpy as np

def haversine(lat1, lon1, lat2, lon2):
    """Calculates the distance (in km) between user and merchant."""
    R = 6371.0
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = np.sin(dlat / 2)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon / 2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return R * c

print("Loading Kaggle Dataset...")
df = pd.read_csv("D:\\indore\\poison-guard-monorepo-s\\data\\fraudTest.csv", nrows=1000)

print("Calculating Geospatial Distances...")
df['distance_km'] = df.apply(lambda row: haversine(row['lat'], row['long'], row['merch_lat'], row['merch_long']), axis=1)

# Grab 5 frauds and 15 clean rows for a quick 20-row demo
fraud_rows = df[df['is_fraud'] == 1].head(5)
normal_rows = df[df['is_fraud'] == 0].head(15)
demo_df = pd.concat([normal_rows, fraud_rows]).sample(frac=1).reset_index(drop=True)

print("Normalizing features for Neural Network...")
# We normalize so the Neural Network math doesn't explode
demo_df['feat1'] = demo_df['amt'] / 1000.0          # Normalized Amount
demo_df['feat2'] = demo_df['distance_km'] / 100.0   # Normalized Distance
demo_df['risk_score'] = demo_df['is_fraud']         # The True Label

demo_df[['feat1', 'feat2', 'risk_score']].to_csv("D:\indore\poison-guard-monorepo-s\python_ml_backend\poison_test.csv", index=False)
print("✅ Created clean poison_test.csv ready for the Autoencoder!")