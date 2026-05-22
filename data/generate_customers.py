import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

np.random.seed(42)
random.seed(42)

NUM_CUSTOMERS = 50000
START_DATE = datetime(2025, 1, 1)
END_DATE = datetime(2025, 12, 31)

# ── Realistic channel distributions with VERY different characteristics ──
channels = ['Organic', 'Paid', 'Referral', 'App Store']
channel_weights = [0.25, 0.40, 0.20, 0.15]

products = ['Personal Loan', 'Credit Line', 'BNPL']
product_weights = [0.45, 0.30, 0.25]

regions = ['North', 'South', 'East', 'West', 'International']
region_weights = [0.25, 0.25, 0.20, 0.20, 0.10]

age_groups = ['18-25', '26-35', '36-45', '45+']
age_weights = [0.20, 0.40, 0.25, 0.15]

# ── Channel-specific retention profiles (very different from each other) ──
channel_retention = {
    'Organic':    {'30d': 0.82, '60d': 0.71, '90d': 0.62, '180d': 0.48, '365d': 0.35},
    'Paid':       {'30d': 0.55, '60d': 0.38, '90d': 0.27, '180d': 0.16, '365d': 0.08},
    'Referral':   {'30d': 0.78, '60d': 0.65, '90d': 0.55, '180d': 0.42, '365d': 0.28},
    'App Store':  {'30d': 0.63, '60d': 0.48, '90d': 0.35, '180d': 0.22, '365d': 0.12},
}

# ── Product-specific loan amounts (wide ranges) ──
product_loan_ranges = {
    'Personal Loan': (50000,  1000000),
    'Credit Line':   (10000,  500000),
    'BNPL':          (2000,   50000),
}

# ── Product-specific LTV multipliers (very different) ──
product_ltv_multiplier = {
    'Personal Loan': (8000,  50000),
    'Credit Line':   (3000,  20000),
    'BNPL':          (500,   5000),
}

# ── Channel-specific LTV ranges (very different) ──
channel_ltv_boost = {
    'Organic':   1.8,
    'Referral':  1.5,
    'App Store': 1.0,
    'Paid':      0.6,
}

# ── Region-specific multipliers ──
region_multiplier = {
    'North': 1.2,
    'South': 1.1,
    'East':  0.9,
    'West':  1.0,
    'International': 1.4,
}

print("Generating 50,000 customers...")

date_range = (END_DATE - START_DATE).days
acquisition_dates = [
    START_DATE + timedelta(days=random.randint(0, date_range))
    for _ in range(NUM_CUSTOMERS)
]

channels_list   = np.random.choice(channels, NUM_CUSTOMERS, p=channel_weights)
products_list   = np.random.choice(products, NUM_CUSTOMERS, p=product_weights)
regions_list    = np.random.choice(regions, NUM_CUSTOMERS, p=region_weights)
age_groups_list = np.random.choice(age_groups, NUM_CUSTOMERS, p=age_weights)

# ── Loan amounts with wide realistic ranges ──
loan_amounts = []
for p in products_list:
    low, high = product_loan_ranges[p]
    # Log-normal distribution for realistic skew
    amount = np.random.lognormal(
        mean=np.log((low + high) / 2),
        sigma=0.6
    )
    amount = np.clip(amount, low, high)
    loan_amounts.append(round(amount, -2))

# ── LTV with huge variance between channels and products ──
ltv_values = []
for i in range(NUM_CUSTOMERS):
    ch = channels_list[i]
    pr = products_list[i]
    rg = regions_list[i]
    base_low, base_high = product_ltv_multiplier[pr]
    base_ltv = np.random.uniform(base_low, base_high)
    ltv = base_ltv * channel_ltv_boost[ch] * region_multiplier[rg]
    # Add noise
    ltv = ltv * np.random.uniform(0.7, 1.3)
    ltv_values.append(round(ltv, 2))

# ── Churn dates based on channel retention profiles ──
TODAY = datetime(2026, 6, 30)
churn_dates = []
is_active_list = []

for i in range(NUM_CUSTOMERS):
    ch = channels_list[i]
    acq_date = acquisition_dates[i]
    days_since = (TODAY - acq_date).days
    ret = channel_retention[ch]

    # Determine if churned based on days since acquisition
    if days_since >= 365:
        churned = np.random.random() > ret['365d']
        if churned:
            churn_day = np.random.randint(1, 365)
            churn_dates.append(acq_date + timedelta(days=churn_day))
            is_active_list.append(False)
        else:
            churn_dates.append(None)
            is_active_list.append(True)
    elif days_since >= 180:
        churned = np.random.random() > ret['180d']
        if churned:
            churn_day = np.random.randint(1, days_since)
            churn_dates.append(acq_date + timedelta(days=churn_day))
            is_active_list.append(False)
        else:
            churn_dates.append(None)
            is_active_list.append(True)
    elif days_since >= 90:
        churned = np.random.random() > ret['90d']
        if churned:
            churn_day = np.random.randint(1, days_since)
            churn_dates.append(acq_date + timedelta(days=churn_day))
            is_active_list.append(False)
        else:
            churn_dates.append(None)
            is_active_list.append(True)
    else:
        churned = np.random.random() > ret['30d']
        if churned:
            churn_day = np.random.randint(1, max(1, days_since))
            churn_dates.append(acq_date + timedelta(days=churn_day))
            is_active_list.append(False)
        else:
            churn_dates.append(None)
            is_active_list.append(True)

# ── Monthly transactions (18 months, very different by channel) ──
txn_cols = {}
channel_txn_rates = {
    'Organic':   (4, 12),
    'Referral':  (3, 10),
    'App Store': (2, 7),
    'Paid':      (1, 4),
}

for month_num in range(18):
    col_name = f'txn_month_{month_num+1}'
    txns = []
    for i in range(NUM_CUSTOMERS):
        ch = channels_list[i]
        acq_date = acquisition_dates[i]
        churn_date = churn_dates[i]
        month_start = START_DATE + timedelta(days=30 * month_num)

        # No transactions before acquisition
        if month_start < acq_date:
            txns.append(0)
        # No transactions after churn
        elif churn_date and month_start > churn_date:
            txns.append(0)
        else:
            low, high = channel_txn_rates[ch]
            # Decay over time — customers become less active
            decay = max(0.3, 1 - (month_num * 0.03))
            base = np.random.randint(low, high)
            txns.append(max(0, int(base * decay * np.random.uniform(0.5, 1.5))))
    txn_cols[col_name] = txns

# ── Build dataframe ──
df = pd.DataFrame({
    'customer_id':        [f'CUST{str(i+1).zfill(5)}' for i in range(NUM_CUSTOMERS)],
    'acquisition_date':   acquisition_dates,
    'acquisition_channel': channels_list,
    'product':            products_list,
    'region':             regions_list,
    'age_group':          age_groups_list,
    'loan_amount':        loan_amounts,
    'first_transaction_date': [
        d + timedelta(days=random.randint(1, 7)) for d in acquisition_dates
    ],
    'churn_date':         churn_dates,
    'is_active':          is_active_list,
    'ltv':                ltv_values,
})

# Add transaction columns
for col, vals in txn_cols.items():
    df[col] = vals

# ── LTV segments ──
df['ltv_segment'] = pd.qcut(
    df['ltv'],
    q=3,
    labels=['Low', 'Medium', 'High']
)

# ── Days since acquisition ──
df['days_since_acquisition'] = (
    pd.Timestamp('2026-06-30') - pd.to_datetime(df['acquisition_date'])
).dt.days

# ── Churn risk flag ──
df['total_recent_txns'] = df[[f'txn_month_{i}' for i in range(16, 19) if f'txn_month_{i}' in df.columns]].sum(axis=1)
df['churn_risk'] = (df['is_active'] == True) & (df['total_recent_txns'] == 0)

# Sort by acquisition date
df = df.sort_values('acquisition_date').reset_index(drop=True)

df.to_csv('data/customers.csv', index=False)
print(f"✅ Dataset generated: {len(df):,} customers")
print(f"\n📊 Channel distribution:")
print(df['acquisition_channel'].value_counts())
print(f"\n💰 LTV by channel (mean):")
print(df.groupby('acquisition_channel')['ltv'].mean().round(0).sort_values(ascending=False))
print(f"\n📦 Product distribution:")
print(df['product'].value_counts())
print(f"\n✅ Active customers: {df['is_active'].sum():,}")
print(f"❌ Churned customers: {(~df['is_active']).sum():,}")
print(f"⚠️  Churn risk: {df['churn_risk'].sum():,}")
