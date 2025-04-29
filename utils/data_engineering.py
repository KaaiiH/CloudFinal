import pandas as pd

def print_available_columns(name, df):
    print(f"Available columns in {name}: {list(df.columns)}")

# Load CSVs
transactions = pd.read_csv('https://smartshopperstorage2.blob.core.windows.net/shopperdata/400_transactions.csv?sp=r&st=2025-04-29T00:54:02Z&se=2025-04-29T08:54:02Z&sv=2024-11-04&sr=b&sig=HaKnknuScoz2dPbPJr96ngMnov4hQcjYmxuCkcDepL4%3D')
products = pd.read_csv('https://smartshopperstorage2.blob.core.windows.net/shopperdata/400_products.csv?sp=r&st=2025-04-29T00:49:32Z&se=2025-05-02T08:49:32Z&sv=2024-11-04&sr=b&sig=8jmyCLbNtHJ5%2F5TsEHw0gj7Lgy90f1skep8D%2Fn8BG2w%3D')
households = pd.read_csv('https://smartshopperstorage2.blob.core.windows.net/shopperdata/400_households.csv?sp=r&st=2025-04-29T00:53:37Z&se=2025-04-29T08:53:37Z&sv=2024-11-04&sr=b&sig=h0vXfgdELpTJzpt46t1PWLNXaMnwruKYAz67z2L3RcU%3D')

# Clean column names
transactions.columns = transactions.columns.str.strip().str.lower()
products.columns = products.columns.str.strip().str.lower()
households.columns = households.columns.str.strip().str.lower()

# Check available columns
print_available_columns("Transactions", transactions)
print_available_columns("Products", products)
print_available_columns("Households", households)

# Rename transaction columns
transactions = transactions.rename(columns={
    'hshd_num': 'household_key',
    'product_num': 'product_id',
    'spend': 'sales_value'
})

# Rename household columns
households = households.rename(columns={
    'hshd_num': 'household_key'
})

# Rename product columns
products = products.rename(columns={
    'product_num': 'product_id'
})

# Verify critical columns exist
required_transactions_cols = ['household_key', 'product_id', 'sales_value']
required_households_cols = ['household_key']
required_products_cols = ['product_id']

for col in required_transactions_cols:
    if col not in transactions.columns:
        raise KeyError(f"Missing required column '{col}' in Transactions data")

for col in required_households_cols:
    if col not in households.columns:
        raise KeyError(f"Missing required column '{col}' in Households data")

for col in required_products_cols:
    if col not in products.columns:
        raise KeyError(f"Missing required column '{col}' in Products data")

# Fill missing values
transactions['sales_value'] = transactions['sales_value'].fillna(0)
products['commodity'] = products['commodity'].fillna('Unknown')

# Merge datasets
merged_df = transactions.merge(households, on='household_key', how='left')
merged_df = merged_df.merge(products, on='product_id', how='left')

# Save merged data
merged_df.to_csv('merged_data.csv', index=False)

print("✅ Merged dataset created successfully: merged_data.csv")
