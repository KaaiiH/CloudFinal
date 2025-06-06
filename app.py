# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import ast
import datetime
import re
from ast import literal_eval

# Load datasets
merged = pd.read_parquet('https://smartshopperstorage2.blob.core.windows.net/shopperdata/merged-data.parquet?sp=r&st=2025-04-29T20:46:02Z&se=2025-05-09T04:46:02Z&sv=2024-11-04&sr=b&sig=k3fU5H5ZCngP9JGAquexh%2BS1zm0PU3YDrj6br2vBbFw%3D')
merged['household_key'] = merged['household_key'].astype('Int64')

clv = pd.read_csv('https://smartshopperstorage2.blob.core.windows.net/shopperdata/clv_predictions.csv?sp=r&st=2025-04-29T20:03:13Z&se=2025-05-09T04:03:13Z&sv=2024-11-04&sr=b&sig=K22lOkM%2BBwGXJURDsWhwbIC78qxefFEl3%2BX%2FwAoO%2B7w%3D')
basket_rules = pd.read_csv('https://smartshopperstorage2.blob.core.windows.net/shopperdata/basket_rules.csv?sp=r&st=2025-04-29T20:02:45Z&se=2025-05-09T04:02:45Z&sv=2024-11-04&sr=b&sig=FH5c35XC60zOpKSTASgk%2BS6A20ijXZ%2FmnWYuKBgNTIE%3D')
products = pd.read_csv('https://smartshopperstorage2.blob.core.windows.net/shopperdata/400_products.csv?sp=r&st=2025-04-29T20:01:51Z&se=2025-05-09T04:01:51Z&sv=2024-11-04&sr=b&sig=eeYaLLXYK7R0fvOBIykfdaPqChHUfTbMo1SqOB2au%2BQ%3D')
products.columns = products.columns.str.strip().str.lower()
products = products.rename(columns={'product_num': 'product_id'})
product_lookup = products.set_index('product_id')['commodity'].to_dict()


# Clean column names
merged.columns = merged.columns.str.strip().str.lower()
clv.columns = clv.columns.str.strip().str.lower()
basket_rules.columns = basket_rules.columns.str.strip().str.lower()

# preprocessing basket_rules to clean frozenset text
def clean_frozenset_text(text):
    try:
        items = list(literal_eval(text))
        return ', '.join(str(item) for item in items)
    except Exception:
        return text

basket_rules['antecedents'] = basket_rules['antecedents'].apply(clean_frozenset_text)
basket_rules['consequents'] = basket_rules['consequents'].apply(clean_frozenset_text)

# treamlit Settings
st.set_page_config(page_title="Smart Shopper Insights", layout="wide")

# Login Page
st.title("Smart Shopper - Login")

username = st.text_input("Username")
password = st.text_input("Password", type="password")
email = st.text_input("Email")


if st.button("Login"):
    st.success(f"Welcome {username}!")
    st.session_state['logged_in'] = True

if st.session_state.get('logged_in', False):

    st.title("🛍️ Smart Shopper Insights Dashboard")
    st.markdown("---")

    # Sidebar for Data Upload
    st.sidebar.header("Upload New Datasets")

    uploaded_transactions = st.sidebar.file_uploader("Upload Transactions CSV")
    uploaded_households = st.sidebar.file_uploader("Upload Households CSV")
    uploaded_products = st.sidebar.file_uploader("Upload Products CSV")

    if st.sidebar.button("Load New Data"):
        if uploaded_transactions and uploaded_households and uploaded_products:
            merged = pd.read_csv(uploaded_transactions)
            households = pd.read_csv(uploaded_households)
            products = pd.read_csv(uploaded_products)
            st.success("New data loaded successfully!")

    # Top KPIs
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    with kpi1:
        st.metric(label="Total Households", value=f"{merged['household_key'].nunique()}")
    with kpi2:
        st.metric(label="Total Transactions", value=f"{len(merged):,}")
    with kpi3:
        avg_spend = merged['sales_value'].mean()
        st.metric(label="Avg Spend per Transaction", value=f"${avg_spend:.2f}")
    with kpi4:
        avg_clv = clv['predicted_clv'].mean()
        st.metric(label="Avg Predicted CLV", value=f"${avg_clv:,.2f}")

    st.markdown("---")

    # Search Household
    st.header("🔍 Search Household Data")
    hshd_search = st.text_input("Enter Household Number to Search")

    if hshd_search:
        try:
            hshd_search_int = int(hshd_search)
            filtered_data = merged[merged['household_key'] == hshd_search_int]
            st.write(filtered_data.sort_values(by=['household_key', 'basket_num', 'year', 'week_num', 'product_id']))
        except ValueError:
            st.error("Please enter a valid number.")

    # Select Household for Dashboard
    st.header("🏠 Explore Selected Household Data")
    selected_household = st.selectbox("Select Household:", merged['household_key'].unique())

    house_data = merged[merged['household_key'] == selected_household]

    # Charts Row 1
    chart1, chart2 = st.columns(2)

    with chart1:
        st.subheader("Spending by Commodity (Pie Chart)")
        if not house_data.empty:
            category_summary = house_data.groupby('commodity')['sales_value'].sum()
            total_sales = category_summary.sum()
            category_percent = (category_summary / total_sales) * 100
            filtered_category_summary = category_summary[category_percent >= 1]
            filtered_category_summary = category_summary[category_percent >= 1]

            # Plot pie chart
            filtered_category_summary = category_summary[category_percent >= 1]

            # Plot pie chart
            fig1, ax1 = plt.subplots()
            ax1.pie(filtered_category_summary, labels=filtered_category_summary.index, autopct='%1.1f%%', startangle=90)
            ax1.axis('equal')
            st.pyplot(fig1)
        else:
            st.write("No data available.")

    with chart2:
        st.subheader("Top Purchased Products (Bar Chart)")
        if not house_data.empty:
            top_products = house_data['product_id'].value_counts().head(10)
            top_products_named = top_products.rename(index=product_lookup).dropna()
            st.bar_chart(top_products_named)
        else:
            st.write("No data available.")

    # Charts Row 2
    chart3, chart4 = st.columns(2)

    
    with chart3:
        st.subheader("Monthly Spending Trend (Line Chart)")
        def convert_year_week_to_date(row):
            try:
                return datetime.datetime.strptime(f"{int(row['year'])}-{int(row['week_num'])}-1", "%Y-%W-%w")
            except:
                return pd.NaT
        if not house_data.empty:
            house_data['purchase_month'] = house_data.apply(convert_year_week_to_date, axis=1)
            monthly_spending = house_data.groupby(house_data['purchase_month'].dt.to_period('M'))['sales_value'].sum()
            monthly_spending.index = monthly_spending.index.astype(str)
            st.line_chart(monthly_spending)
        else:
            st.write("No data available.")
    with chart4:
        st.subheader("Top Product Bundles (Lift)")
        st.caption("Lift > 1 means stronger buying relationship between products.")

        if not basket_rules.empty:
            top_rules = basket_rules.sort_values(by='lift', ascending=False).head(5)

            def get_name(pid):
                return product_lookup.get(int(pid), f"Product {pid}")
            
            for idx, row in top_rules.iterrows():
                antecedents = row['antecedents']
                consequents = row['consequents']

                antecedents = antecedents.replace(" ", "")
                clean_ant = re.sub(r'[a-z(){}]', '', antecedents)
                clean_ant = clean_ant.split(",")

                consequents = consequents.replace(" ", "")
                clean_con = re.sub(r'[a-z(){}]', '', consequents)
                clean_con = clean_con.split(",")

                

                if len(clean_ant) > 1:
                    ant_names = [get_name(p) for p in clean_ant[:2]]
                    con_name = get_name(clean_con[0])
                    st.markdown(f"👉 **If someone buys** {ant_names[0]} or {ant_names[1]} **→ Recommend** _{con_name}_ (**Lift: {row['lift']:.2f}**)")
                else:
                    ant_name = get_name(clean_ant[0])
                    con_name = get_name(clean_con[0])
                    st.markdown(f"👉 **If someone buys** _{ant_name}_ **→ Recommend** _{con_name}_ (**Lift: {row['lift']:.2f}**)")

        else:
            st.write("No basket analysis data available.")

    # Churn Prediction
    st.header("⚠️ Churn Prediction Analysis")

    st.caption("Customers spending less over time may be at risk of disengaging.")

    if selected_household:
        if not house_data.empty and 'purchase_month' in house_data.columns:
            spending_by_month = house_data.groupby(house_data['purchase_month'].dt.to_period('M'))['sales_value'].sum()
            spending_by_month.index = spending_by_month.index.astype(str)
            st.line_chart(spending_by_month)

            if len(spending_by_month) > 1:
                if spending_by_month.iloc[-1] < spending_by_month.iloc[0]:
                    st.warning("This household's spending has decreased over time. Risk of churn detected!")
                else:
                    st.success("This household's spending has been stable or increasing.")
        else:
            st.write("Not enough monthly data available for churn prediction.")
