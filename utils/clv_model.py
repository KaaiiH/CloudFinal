# clv_model.py
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score

# Load the merged data
df = pd.read_parquet('https://smartshopperstorage2.blob.core.windows.net/shopperdata/merged-data.parquet?sp=r&st=2025-04-29T20:46:02Z&se=2025-05-09T04:46:02Z&sv=2024-11-04&sr=b&sig=k3fU5H5ZCngP9JGAquexh%2BS1zm0PU3YDrj6br2vBbFw%3D')

# Aggregate features per household
features = df.groupby('household_key').agg({
    'sales_value': 'sum',
    'product_id': 'count'
}).reset_index()

# Rename features
features.columns = ['household_key', 'total_spent', 'num_products']

# Generate a proxy for CLV
features['clv'] = features['total_spent'] * 1.15

# Prepare X (features) and y (target)
X = features[['total_spent', 'num_products']]
y = features['clv']

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = RandomForestRegressor()
model.fit(X_train, y_train)

# Predict and evaluate
y_pred = model.predict(X_test)
print(f"✅ Model R² Score: {r2_score(y_test, y_pred):.2f}")

# Save predictions
features['predicted_clv'] = model.predict(X)
features[['household_key', 'predicted_clv']].to_csv('clv_predictions.csv', index=False)

print("✅ CLV predictions saved to clv_predictions.csv")
