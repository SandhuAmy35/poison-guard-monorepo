import pandas as pd

# Create a mix of clean data and poisoned outliers
data = {
    'feat1': [0.12, 0.15, 0.11, 0.88, 0.92],
    'feat2': [0.22, 0.25, 0.21, 0.77, 0.81],
    'risk_score': [0.10, 0.15, 0.12, 0.95, 0.99] # Last two will trigger the Shadow Model
}

df = pd.DataFrame(data)
df.to_csv("poison_test.csv", index=False)
print("✅ poison_test.csv generated successfully!")