import pandas as pd
import numpy as np

print("Loading Real-World Credit Dataset...")
df = pd.read_csv(r"D:\indore\poison-guard-monorepo-s\data\credit_score.csv")

# We select the most important features for credit risk
# Feature 1: Normalized Income
# Feature 2: Debt-to-Income Ratio (Classic banking metric)
print("Processing Credit Manifold...")

df['feat1'] = df['INCOME'] / df['INCOME'].max()  # Scale income 0 to 1
df['feat2'] = df['R_DEBT_INCOME'] / 20.0        # Normalize the ratio
df['risk_score'] = df['DEFAULT']                 # Ground Tuth label

# Select a mix of 20 rows for the demo
defaulters = df[df['DEFAULT'] == 1].head(5)
clean_payers = df[df['DEFAULT'] == 0].head(15)
demo_df = pd.concat([defaulters, clean_payers]).sample(frac=1).reset_index(drop=True)

demo_df[['feat1', 'feat2', 'risk_score']].to_csv("credit_test.csv", index=False)
print("✅ Created credit_test.csv! Your backend now supports Credit Domain Profiles.")