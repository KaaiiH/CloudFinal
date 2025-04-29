import pandas as pd
from mlxtend.frequent_patterns import fpgrowth, association_rules

# Load transactions data
transactions = pd.read_csv('https://smartshopperstorage2.blob.core.windows.net/shopperdata/400_transactions.csv?sp=r&st=2025-04-29T20:01:27Z&se=2025-05-09T04:01:27Z&sv=2024-11-04&sr=b&sig=yKOgzNbGmCh0aoletCWOPIAMwV6du0gcnXUhvQn7nn0%3D')

# Clean column names
transactions.columns = transactions.columns.str.strip().str.lower()

# Prepare the basket
basket = (transactions.groupby(['hshd_num', 'product_num'])['spend']
          .sum().unstack().fillna(0))

# Convert to Boolean
basket = basket > 0

# Keep only popular products
basket = basket.loc[:, basket.sum() > 10]

# Limit to top 100 most purchased products
top_products = basket.sum().sort_values(ascending=False).head(100).index
basket = basket[top_products]

# Apply FP-Growth with higher min_support
frequent_itemsets = fpgrowth(basket, min_support=0.3, use_colnames=True)

# Generate association rules
rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1)

# Save results
rules.to_csv('basket_rules.csv', index=False)

print("✅ Basket analysis (FP-Growth) completed and saved to basket_rules.csv")
