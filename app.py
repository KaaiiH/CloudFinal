# app.py
import streamlit as st
# treamlit Settings
st.set_page_config(page_title="Smart Shopper Insights", layout="wide")

import pandas as pd
import matplotlib.pyplot as plt
import re
from ast import literal_eval

# --- User Authentication ---
login_placeholder = st.empty()
with login_placeholder.container():
    st.subheader("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    email = st.text_input("Email")
    login_button = st.button("Login")

if not login_button or not username:
    st.stop()

login_placeholder.empty()

# --- Load Data with Upload Option ---
st.sidebar.header("📤 Upload New Data")
tx_file = st.sidebar.file_uploader("Upload Transactions CSV", type=["csv"])
prod_file = st.sidebar.file_uploader("Upload Products CSV", type=["csv"])
hh_file = st.sidebar.file_uploader("Upload Households CSV", type=["csv"])

# Load datasets
@st.cache_data(ttl=3600)
def load_data():
    transactions = pd.read_csv('https://smartshopperstorage2.blob.core.windows.net/shopperdata/400_transactions.csv?sp=r&st=2025-04-29T20:01:27Z&se=2025-05-09T04:01:27Z&sv=2024-11-04&sr=b&sig=yKOgzNbGmCh0aoletCWOPIAMwV6du0gcnXUhvQn7nn0%3D')
    products = pd.read_csv('https://smartshopperstorage2.blob.core.windows.net/shopperdata/400_products.csv?sp=r&st=2025-04-29T20:01:51Z&se=2025-05-09T04:01:51Z&sv=2024-11-04&sr=b&sig=eeYaLLXYK7R0fvOBIykfdaPqChHUfTbMo1SqOB2au%2BQ%3D')
    households = pd.read_csv('https://smartshopperstorage2.blob.core.windows.net/shopperdata/400_households.csv?sp=r&st=2025-04-29T20:02:10Z&se=2025-05-09T04:02:10Z&sv=2024-11-04&sr=b&sig=CXJEA0IyaYJrHrj0E7gv9z34LMBPvZwWNMXQTUMVzJc%3D')
    clv = pd.read_csv('https://smartshopperstorage2.blob.core.windows.net/shopperdata/clv_predictions.csv?sp=r&st=2025-04-29T20:03:13Z&se=2025-05-09T04:03:13Z&sv=2024-11-04&sr=b&sig=K22lOkM%2BBwGXJURDsWhwbIC78qxefFEl3%2BX%2FwAoO%2B7w%3D')
    basket_rules = pd.read_csv('https://smartshopperstorage2.blob.core.windows.net/shopperdata/basket_rules.csv?sp=r&st=2025-04-29T20:02:45Z&se=2025-05-09T04:02:45Z&sv=2024-11-04&sr=b&sig=FH5c35XC60zOpKSTASgk%2BS6A20ijXZ%2FmnWYuKBgNTIE%3D')

    
    # Clean column names
    transactions.columns = transactions.columns.str.strip().str.lower()
    products.columns = products.columns.str.strip().str.lower()
    households.columns = households.columns.str.strip().str.lower()
    clv.columns = clv.columns.str.strip().str.lower()
    basket_rules.columns = basket_rules.columns.str.strip().str.lower()

    return transactions, products, households, clv, basket_rules

transactions, products, households, clv, basket_rules = load_data()

#build lookup for products
products = products.rename(columns={'product_num': 'product_id'})
product_lookup = products.set_index('product_id')['commodity'].to_dict()


# --- Top KPIs ---
st.title("🛍️ Smart Shopper Insights Dashboard")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.metric("Total Households", value=f"{transactions['hshd_num'].nunique()}")
with kpi2:
    st.metric("Total Transactions", value=f"{len(transactions):,}")
with kpi3:
    st.metric("Avg Spend per Transaction", value=f"${transactions['spend'].mean():.2f}")
with kpi4:
    st.metric("Avg Predicted CLV", value=f"${clv['predicted_clv'].mean():,.2f}")

st.markdown("---")

# --- Household Exploration ---
st.header("🔍 Explore Household Data")
selected_household = st.selectbox("Select Household", transactions['hshd_num'].unique())
filtered = transactions[transactions['hshd_num'] == selected_household]
filtered = filtered.merge(products, left_on='product_num', right_index=True, how='left')
filtered = filtered.merge(households, on='hshd_num', how='left')


# --- Charts Row 1 ---
chart1, chart2 = st.columns(2)
with chart1:
    st.subheader("Spending by Commodity (Pie Chart)")
    if not filtered.empty:
        summary = filtered.groupby('commodity')['spend'].sum()
        filtered_summary = summary[(summary / summary.sum()) * 100 >= 1]
        fig1, ax1 = plt.subplots()
        ax1.pie(filtered_summary, labels=filtered_summary.index, autopct='%1.1f%%', startangle=90)
        ax1.axis('equal')
        st.pyplot(fig1)
with chart2:
    st.subheader("Top Purchased Products (Bar Chart)")
    if not filtered.empty:
        top_products = filtered['product_id'].value_counts().head(10)
        st.bar_chart(top_products)

# --- Charts Row 2 ---
chart3, chart4 = st.columns(2)
with chart3:
    st.subheader("Monthly Spending Trend (Line Chart)")
    if not filtered.empty:
        filtered['purchase_month'] = pd.to_datetime(filtered['year'].astype(str) + '-' + filtered['week_num'].astype(str) + '-1', errors='coerce')
        trend = filtered.groupby(filtered['purchase_month'].dt.to_period('M'))['spend'].sum()
        st.line_chart(trend)
with chart4:
    st.subheader("Top Product Bundles (Lift)")
    if not basket_rules.empty:
        for _, row in basket_rules.sort_values(by='lift', ascending=False).head(5).iterrows():
            ant = re.sub(r'[^0-9,]', '', row['antecedents']).split(',')
            con = re.sub(r'[^0-9,]', '', row['consequents']).split(',')
            if len(ant) > 1:
                st.markdown(f"👉 If {ant[0]} or {ant[1]} → Recommend {con[0]} (Lift: {row['lift']:.2f})")
            else:
                st.markdown(f"👉 If {ant[0]} → Recommend {con[0]} (Lift: {row['lift']:.2f})")

# --- Churn Prediction ---
st.header("📉 Churn Risk Analysis")
churn_data = transactions.groupby('hshd_num').agg({
    'week_num': 'max',
    'spend': 'sum'
}).reset_index()
churn_data['is_churned'] = churn_data['week_num'] < 40

fig, ax = plt.subplots()
ax.plot(churn_data['week_num'], churn_data['spend'], label='Total Spend')
ax.set_title("Spending vs. Week Number")
ax.set_xlabel("Week Number")
ax.set_ylabel("Total Spend")
st.pyplot(fig)