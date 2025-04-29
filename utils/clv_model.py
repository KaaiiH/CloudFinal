import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score

# Load transactions and households
transactions = pd.read_csv('https://smartshopperstorage2.blob.core.windows.net/shopperdata/400_transactions.csv?sp=r&st=2025-04-29T20:01:27Z&se=2025-05-09T04:01:27Z&sv=2024-11-04&sr=b&sig=yKOgzNbGmCh0aoletCWOPIAMwV6du0gcnXUhvQn7nn0%3D')
households = pd.read_csv('https://smartshopperstorage2.blob.core.windows.net/shopperdata/400_households.csv?sp=r&st=2025-04-29T20:02:10Z&se=2025-05-09T04:02:10Z&sv=2024-11-04&sr=b&sig=CXJEA0IyaYJrHrj0E7gv9z34LMBPvZwWNMXQTUMVzJc%3D')

# Clean column names
transactions.columns = transactions.columns.str.strip().str.lower()
households.columns = households.columns.str.strip().str.lower()

# Rename for consistency
transactions = transactions.rename(columns={'hshd_num': 'household_key', 'spend': 'sales_value'})
households = households.rename(columns={'hshd_num': 'household_key'})

# Aggregate features per household
features = transactions.groupby('household_key').agg({
    'sales_value': 'sum',
    'basket_num': 'nunique'
}).reset_index()

# Rename features
features.columns = ['household_key', 'total_spent', 'num_baskets']

# Generate a proxy for CLV
features['clv'] = features['total_spent'] * 1.15

# Prepare X (features) and y (target)
X = features[['total_spent', 'num_baskets']]
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
