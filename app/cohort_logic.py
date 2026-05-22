import pandas as pd
import streamlit as st

@st.cache_data
def load_data():
    df = pd.read_csv('data/customers.csv', parse_dates=['acquisition_date'])
    df['churn_date'] = pd.to_datetime(df['churn_date'], errors='coerce')
    df['cohort_month'] = df['acquisition_date'].dt.to_period('M').astype(str)
    return df

def filter_data(df, channels, products, regions):
    mask = (
        df['acquisition_channel'].isin(channels) &
        df['product'].isin(products) &
        df['region'].isin(regions)
    )
    return df[mask]

def build_cohort_matrix(df):
    today = pd.Timestamp('2026-06-30')
    cohorts = df.groupby('cohort_month')

    records = []
    for cohort, group in cohorts:
        size = len(group)
        if size == 0:
            continue
        for period, days in [('30d', 30), ('60d', 60), ('90d', 90), ('180d', 180), ('365d', 365)]:
            cutoff = group['acquisition_date'] + pd.Timedelta(days=days)
            retained = group[
                (group['churn_date'].isna()) |
                (group['churn_date'] > cutoff)
            ]
            pct = round(len(retained) / size * 100, 1)
            records.append({'cohort': cohort, 'period': period, 'retention_pct': pct})

    pivot = pd.DataFrame(records).pivot(
        index='cohort',
        columns='period',
        values='retention_pct'
    )
    # Reorder columns
    col_order = ['30d', '60d', '90d', '180d', '365d']
    pivot = pivot[[c for c in col_order if c in pivot.columns]]
    return pivot

def calculate_kpis(df):
    total = len(df)
    active = df['is_active'].sum() if df['is_active'].dtype == bool else (df['is_active'] == True).sum()
    churned = total - active
    return {
        'total_customers': total,
        'active_customers': int(active),
        'churn_rate': round(churned / total * 100, 1) if total > 0 else 0,
        'retention_rate': round(active / total * 100, 1) if total > 0 else 0,
        'avg_ltv': round(df['ltv'].mean(), 0),
        'total_ltv': round(df['ltv'].sum(), 0),
        'high_value_customers': int((df['ltv_segment'] == 'High').sum()),
        'churn_risk_count': int(df['churn_risk'].sum()) if 'churn_risk' in df.columns else 0
    }

def get_retention_by_channel(df):
    result = []
    for channel in df['acquisition_channel'].unique():
        ch_df = df[df['acquisition_channel'] == channel]
        for period, days in [('30d', 30), ('60d', 60), ('90d', 90), ('180d', 180), ('365d', 365)]:
            cutoff = ch_df['acquisition_date'] + pd.Timedelta(days=days)
            retained = ch_df[
                (ch_df['churn_date'].isna()) |
                (ch_df['churn_date'] > cutoff)
            ]
            pct = round(len(retained) / len(ch_df) * 100, 1) if len(ch_df) > 0 else 0
            result.append({'channel': channel, 'period': period, 'retention_pct': pct})
    return pd.DataFrame(result)
