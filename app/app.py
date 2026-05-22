import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from cohort_logic import (
    load_data, filter_data, build_cohort_matrix,
    calculate_kpis, get_retention_by_channel
)

# ── Page Config ──────────────────────────────────
st.set_page_config(
    page_title="ClearLend — Cohort & Retention Analytics",
    page_icon="🏦",
    layout="wide"
)

# ── Load Data ────────────────────────────────────
df = load_data()

# ── Sidebar ──────────────────────────────────────
st.sidebar.image("https://img.icons8.com/color/96/bank.png", width=55)
st.sidebar.title("ClearLend Analytics")
st.sidebar.markdown("---")

channels = st.sidebar.multiselect(
    "Acquisition Channel",
    options=df['acquisition_channel'].unique().tolist(),
    default=df['acquisition_channel'].unique().tolist()
)
products = st.sidebar.multiselect(
    "Product",
    options=df['product'].unique().tolist(),
    default=df['product'].unique().tolist()
)
regions = st.sidebar.multiselect(
    "Region",
    options=df['region'].unique().tolist(),
    default=df['region'].unique().tolist()
)

# ── Filter ───────────────────────────────────────
filtered = filter_data(df, channels, products, regions)

# ── Title ────────────────────────────────────────
st.title("🏦 ClearLend — Customer Cohort & Retention Dashboard")
st.markdown("Tracking 30-day to 1-year retention, LTV segmentation and churn risk across 50K+ customers")
st.markdown("---")

# ── SECTION 1: KPI Cards ─────────────────────────
kpis = calculate_kpis(filtered)
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("👥 Total Customers",   f"{kpis['total_customers']:,}")
k2.metric("✅ Active Customers",  f"{kpis['active_customers']:,}")
k3.metric("📉 Churn Rate",        f"{kpis['churn_rate']}%")
k4.metric("💰 Avg LTV",           f"₹{kpis['avg_ltv']:,.0f}")
k5.metric("⚠️ Churn Risk",        f"{kpis['churn_risk_count']:,}")
st.markdown("---")

# ── SECTION 2: Cohort Retention Heatmap ──────────
st.subheader("🟩 Cohort Retention Heatmap")
st.caption("Each cell shows % of that month's cohort still active at that period")

cohort_matrix = build_cohort_matrix(filtered)

if not cohort_matrix.empty:
    fig_heat = px.imshow(
        cohort_matrix,
        color_continuous_scale='RdYlGn',
        text_auto=True,
        aspect='auto',
        labels=dict(x="Retention Period", y="Acquisition Cohort", color="Retention %"),
        zmin=0, zmax=100
    )
    fig_heat.update_layout(
        height=450,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        coloraxis_colorbar=dict(title="Ret %")
    )
    fig_heat.update_traces(textfont=dict(size=13, color='white'))
    st.plotly_chart(fig_heat, use_container_width=True)
st.markdown("---")

# ── SECTION 3: Retention Curves by Channel ───────
st.subheader("📈 Retention Curves by Acquisition Channel")
st.caption("How each channel retains customers over time — Organic vs Paid vs Referral vs App Store")

channel_ret = get_retention_by_channel(filtered)
period_order = ['30d', '60d', '90d', '180d', '365d']
channel_ret['period'] = pd.Categorical(channel_ret['period'], categories=period_order, ordered=True)
channel_ret = channel_ret.sort_values('period')

fig_curves = px.line(
    channel_ret,
    x='period', y='retention_pct',
    color='channel',
    markers=True,
    labels={'period': 'Days Since Acquisition', 'retention_pct': 'Retention %', 'channel': 'Channel'},
    color_discrete_map={
        'Organic':   '#52b788',
        'Referral':  '#4361ee',
        'App Store': '#f77f00',
        'Paid':      '#e63946'
    }
)
fig_curves.update_layout(
    height=380,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='white'),
    yaxis=dict(range=[0, 100], gridcolor='#252a3d'),
    xaxis=dict(gridcolor='#252a3d'),
    legend=dict(bgcolor='rgba(0,0,0,0)')
)
fig_curves.update_traces(line=dict(width=3), marker=dict(size=9))
st.plotly_chart(fig_curves, use_container_width=True)
st.markdown("---")

# ── SECTION 4: LTV by Channel + Product ──────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("💰 Avg LTV by Channel")
    ltv_channel = filtered.groupby('acquisition_channel')['ltv'].mean().reset_index()
    ltv_channel.columns = ['channel', 'avg_ltv']
    ltv_channel = ltv_channel.sort_values('avg_ltv', ascending=True)
    fig_ltv_ch = px.bar(
        ltv_channel, x='avg_ltv', y='channel',
        orientation='h',
        color='avg_ltv',
        color_continuous_scale='Blues',
        text=ltv_channel['avg_ltv'].apply(lambda x: f"₹{x:,.0f}")
    )
    fig_ltv_ch.update_layout(
        height=320,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        showlegend=False,
        coloraxis_showscale=False,
        xaxis=dict(gridcolor='#252a3d'),
        yaxis=dict(gridcolor='#252a3d')
    )
    fig_ltv_ch.update_traces(textposition='outside', textfont=dict(color='white'))
    st.plotly_chart(fig_ltv_ch, use_container_width=True)

with col2:
    st.subheader("📦 Avg LTV by Product")
    ltv_product = filtered.groupby('product')['ltv'].mean().reset_index()
    ltv_product.columns = ['product', 'avg_ltv']
    ltv_product = ltv_product.sort_values('avg_ltv', ascending=True)
    fig_ltv_pr = px.bar(
        ltv_product, x='avg_ltv', y='product',
        orientation='h',
        color='avg_ltv',
        color_continuous_scale='Greens',
        text=ltv_product['avg_ltv'].apply(lambda x: f"₹{x:,.0f}")
    )
    fig_ltv_pr.update_layout(
        height=320,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        showlegend=False,
        coloraxis_showscale=False,
        xaxis=dict(gridcolor='#252a3d'),
        yaxis=dict(gridcolor='#252a3d')
    )
    fig_ltv_pr.update_traces(textposition='outside', textfont=dict(color='white'))
    st.plotly_chart(fig_ltv_pr, use_container_width=True)

st.markdown("---")

# ── SECTION 5: LTV Segmentation ──────────────────
col3, col4 = st.columns(2)

with col3:
    st.subheader("🎯 LTV Segmentation")
    seg_counts = filtered['ltv_segment'].value_counts().reset_index()
    seg_counts.columns = ['segment', 'count']
    fig_seg = px.pie(
        seg_counts, values='count', names='segment',
        color='segment',
        color_discrete_map={
            'High':   '#52b788',
            'Medium': '#f77f00',
            'Low':    '#e63946'
        },
        hole=0.45
    )
    fig_seg.update_layout(
        height=320,
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        legend=dict(bgcolor='rgba(0,0,0,0)')
    )
    fig_seg.update_traces(textinfo='percent+label', textfont_size=13)
    st.plotly_chart(fig_seg, use_container_width=True)

with col4:
    st.subheader("📊 Cohort Size by Month")
    cohort_size = filtered.groupby('cohort_month').size().reset_index()
    cohort_size.columns = ['cohort_month', 'customers']
    fig_size = px.bar(
        cohort_size, x='cohort_month', y='customers',
        color='customers',
        color_continuous_scale='Blues',
        text='customers'
    )
    fig_size.update_layout(
        height=320,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        showlegend=False,
        coloraxis_showscale=False,
        xaxis=dict(gridcolor='#252a3d', tickangle=45),
        yaxis=dict(gridcolor='#252a3d')
    )
    fig_size.update_traces(textposition='outside', textfont=dict(color='white', size=10))
    st.plotly_chart(fig_size, use_container_width=True)

st.markdown("---")

# ── SECTION 6: Churn Risk Table ───────────────────
st.subheader("⚠️ High Churn Risk Customers")
st.caption("Active customers with zero recent transactions — sorted by LTV (highest value at risk first)")

churn_risk_df = filtered[
    (filtered['is_active'] == True) &
    (filtered['churn_risk'] == True)
][['customer_id', 'acquisition_channel', 'product', 'region',
   'age_group', 'acquisition_date', 'ltv', 'ltv_segment', 'loan_amount']]\
  .sort_values('ltv', ascending=False)\
  .head(50)

churn_risk_df['ltv'] = churn_risk_df['ltv'].apply(lambda x: f"₹{x:,.0f}")
churn_risk_df['loan_amount'] = churn_risk_df['loan_amount'].apply(lambda x: f"₹{x:,.0f}")

st.dataframe(churn_risk_df.reset_index(drop=True), use_container_width=True)
