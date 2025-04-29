import pandas as pd
from mlxtend.frequent_patterns import fpgrowth, association_rules

# Load merged data
df = pd.read_csv('https://smartshopperstorage2.blob.core.windows.net/shopperdata/merged_data.csv?sp=r&st=2025-04-29T00:52:21Z&se=2025-04-29T08:52:21Z&sv=2024-11-04&sr=b&sig=UERZtZKYx0ArXShOpF5G00Kb2zz1q0VwS8uNfiauwbQ%3D')

# Prepare the basket
basket = (df.groupby(['household_key', 'product_id'])['sales_value']
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
