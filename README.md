# 🛒 Smart Shopper Insights Dashboard

## Overview
Smart Shopper Insights is a full-stack cloud-based dashboard built on Azure that enables retailers to analyze customer behavior, predict Customer Lifetime Value (CLV), explore basket analysis, and detect churn risks. The project focuses on providing actionable insights into customer engagement and spending trends.

This project demonstrates the ability to build an end-to-end data pipeline with machine learning modeling, cloud deployment, and interactive visualizations using Azure services.

---

## Key Features
- **Secure Login Page** with Username, Password, and Email fields
- **Upload New Retail Datasets** (Transactions, Households, Products) directly through the web app
- **Customer Data Explorer**: Search for households by HSHD_NUM
- **Interactive Dashboards**:
  - Household spending breakdown (Pie Chart, Bar Chart)
  - Monthly spending trends (Line Chart)
  - Top Product Bundles for cross-sell opportunities (Lift metric)
  - Churn Risk Prediction (spending over time analysis)
- **Deployed to Azure App Service** with public access

---

## Machine Learning Models Used
- **Random Forest Regression**:  
  Used to predict Customer Lifetime Value (CLV) based on transaction and household attributes.
- **FP-Growth Frequent Pattern Mining**:  
  Used to identify commonly purchased product bundles and generate cross-selling recommendations.

---

## Technologies
- **Azure Services**: Blob Storage, App Service, Resource Group, Linux Free Plan
- **Python Libraries**: Streamlit, pandas, scikit-learn, mlxtend, matplotlib
- **Deployment CLI**: Azure CLI (`az webapp up`)
- **Interactive Visualization**: Streamlit Web App

---

## Retail Questions Addressed
- **Customer Lifetime Value Prediction**: Prioritize high-value customers for loyalty efforts.
- **Basket Analysis**: Discover product combinations for cross-selling strategies.
- **Churn Prediction**: Identify households at risk of disengaging based on declining spending trends.
- **Household Spending Trends**: Understand customer engagement over time.

---


## Deployment Details
- **App URL**: [https://smartshopperdashboard.azurewebsites.net](https://smartshopperdashboard.azurewebsites.net) *(example URL)*
- **Hosting Platform**: Azure App Service
- **Operating System**: Linux (B1 Pricing Tier)

---

## How to Run Locally
1. Install required libraries:
```pip install -r requirements.txt```

2. Launch Streamlit:
```streamlit run app.py```

---

## Credits
Developed by: Kai Hoenshell & Jacob Bai 
University of Cincinnati  
Cloud Computing Final Project, Spring 2025