# ClearLend — Customer Cohort & Retention Dashboard

![Python](https://img.shields.io/badge/Python-3.10-blue)
![SQL](https://img.shields.io/badge/SQL-DuckDB-orange)
![Streamlit](https://img.shields.io/badge/Streamlit-Live-red)
![Tableau](https://img.shields.io/badge/Tableau-Public-blue)

## 🔗 Live Links
- 🚀 **Streamlit App:** [customer-cohort-retention.streamlit.app](https://customer-cohort-retention.streamlit.app)
- 📊 **Tableau Dashboard:** [ClearLend Retention Dashboard](https://public.tableau.com/app/profile/ajinkya.kadam/viz/ClearLend-CustomerCohertRetentionDashboard/RetentionView)

---

## 📌 Project Overview
ClearLend is a fictional fintech lending platform. This project simulates a real-world customer analytics workflow tracking cohort retention, churn risk, and lifetime value (LTV) across 50,000 customers acquired in 2025.

---

## 📊 Dataset
| Property | Details |
|---|---|
| Rows | 50,000 customers |
| Date Range | Jan 2025 — Dec 2025 (acquisition) |
| Tracked Until | Jun 2026 |
| Channels | Organic, Referral, App Store, Paid |
| Products | Personal Loan, Credit Line, BNPL |
| Regions | North, South, East, West, International |

---

## 🔑 Key Metrics
| Metric | Value |
|---|---|
| Total Customers | 50,000 |
| Active Customers | 12,376 |
| Churn Rate | 75.2% |
| Average LTV | ₹21,396 |
| Churn Risk Customers | 376 |
| Best Channel (LTV) | Organic ₹34K avg |
| Worst Channel (LTV) | Paid ₹11K avg |

---

## 🛠️ Tech Stack
| Tool | Usage |
|---|---|
| Python | Data generation, Streamlit app |
| DuckDB | SQL queries on local dataset |
| Pandas | Data manipulation |
| Plotly | Charts in Streamlit |
| Streamlit | Live interactive web app |
| Tableau | Executive dashboards |
| Figma | Dashboard background design |
| GitHub Codespaces | Cloud development environment |

---

## 📁 Project Structure
├── generate_data.py      # Generates 50,000 rows synthetic dataset
├── queries.sql           # 6 DuckDB SQL queries
├── app.py                # Streamlit app main file
├── utils.py              # Helper functions
├── clearlend_data.csv    # Generated dataset
└── README.md


---

## 📋 SQL Queries
1. Cohort Retention Matrix
2. Churn Rate by Cohort Month
3. LTV by Acquisition Channel
4. Monthly Active Users Trend
5. High Churn Risk Customers
6. LTV Segmentation by Channel and Product

---

## 📊 Tableau Dashboard
Two interactive views published on Tableau Public:
- **Retention View** — Cohort heatmap, retention curves, churn by month
- **LTV View** — LTV distribution, segmentation, summary table

---

## 👨‍💻 Author
**Ajinkya Kadam**
Senior Data Analyst | Pune, India
[LinkedIn](https://linkedin.com/in/ajinkya-kadam) | [Tableau Public](https://public.tableau.com/app/profile/ajinkya.kadam)
