import pandas as pd
import os

BASE = '/home/harshit/Documents/amex'
DATA_PATH = f'{BASE}/6a3eb196bc7a3_campus_challenge_r1_data.csv'
OUT_DIR = f'{BASE}/output'
TEMPLATE_PATH = f'{BASE}/6a3cb64c7cae4_campus_challenge_r1_submission_template.xlsx'

df = pd.read_csv(DATA_PATH)
df_framework = pd.read_excel(TEMPLATE_PATH, sheet_name='Profitability Framework')

# Imputation
risk_median = df['f11'].median()
df['f11'] = df['f11'].fillna(risk_median)
for f in ['f6', 'f7', 'f8', 'f9', 'f10']:
    df[f] = df[f].fillna(0)
for f in ['f1', 'f2', 'f3', 'f4', 'f5', 'f12', 'f13', 'f14', 'f15',
          'f16', 'f17', 'f18', 'f19', 'f20', 'f21', 'f22', 'f23']:
    df[f] = df[f].fillna(0)

def generate_v7_variant(name, APR, PTS_COST_RATE, ECL_MULT, COL_BASE, COL_MULT):
    R_interchange = (df['f6'] + df['f9']) * 0.030 + (df['f7'] + df['f8'] + df['f10']) * 0.020
    R_interest = df['f1'] * APR
    R_supp = df['f19'] * 100.0 + df['f20'] * 100.0
    R_credit_line = df['f17'] * 0.0001
    
    pts_earned = df['f6'] * 5 + df['f9'] * 5 + df['f7'] * 1 + df['f8'] * 1 + df['f10'] * 1
    C_pts_accrual = pts_earned * PTS_COST_RATE
    
    C_lounge = df['f13'] * 40.0
    C_airline = df['f14']
    C_cab = df['f15'] * 15.0
    C_ent = df['f16']
    
    C_ecl = df['f1'] * df['f11'] * ECL_MULT + (df['f3'] * COL_BASE) + (df['f3'] * df['f1'] * COL_MULT)
    C_retention = df['f2'] * 300.0
    
    df['Profitability_Score'] = (
        R_interchange + R_interest + R_supp + R_credit_line
        - C_pts_accrual - C_lounge - C_airline - C_cab - C_ent - C_ecl - C_retention
    )
    
    sub = df[['id', 'Profitability_Score']].rename(columns={'id': 'ID', 'Profitability_Score': 'Prediction'})
    sub = sub.sort_values('ID').reset_index(drop=True)
    
    xlsx_path = f'{OUT_DIR}/submission_{name}.xlsx'
    with pd.ExcelWriter(xlsx_path) as writer:
        sub.to_excel(writer, sheet_name='Predictions', index=False)
        df_framework.to_excel(writer, sheet_name='Profitability Framework', index=False)
    print(f"Generated: {xlsx_path}")

# V7 Baseline reminder:
# APR=0.24, PTS_COST_RATE=0.0075 (1.5c * 50%), ECL_MULT=1.0, COL_BASE=1000, COL_MULT=1.0

# Variant 10: 1 Cent points (100% redemption assumption) & Pure Balance Collection Loss (no base 1000)
generate_v7_variant('v10_one_cent_points_pure_col_loss',
                    APR=0.24, PTS_COST_RATE=0.010, ECL_MULT=1.0, COL_BASE=0.0, COL_MULT=1.0)

# Variant 11: Lower APR Margin (0.20) - Net interest margin is usually lower than raw APR
generate_v7_variant('v11_lower_apr_0_20',
                    APR=0.20, PTS_COST_RATE=0.0075, ECL_MULT=1.0, COL_BASE=1000.0, COL_MULT=1.0)

# Variant 12: Higher ECL Multiplier (1.2) - Defaults usually include late fees and overlimit
generate_v7_variant('v12_higher_ecl_1_2',
                    APR=0.24, PTS_COST_RATE=0.0075, ECL_MULT=1.2, COL_BASE=1000.0, COL_MULT=1.0)

