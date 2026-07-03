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

# Variant 13: Cash Basis (f21) + V7 High Penalties
R_interchange = (df['f6'] + df['f9']) * 0.030 + (df['f7'] + df['f8'] + df['f10']) * 0.020
R_interest = df['f1'] * 0.24
R_supp = df['f19'] * 100.0 + df['f20'] * 100.0
R_credit_line = df['f17'] * 0.0001

# USE CASH BASIS (f21) like in V2 which scored 0.765 without penalties
C_pts_cash = df['f21'] * 0.015

C_lounge = df['f13'] * 40.0
C_airline = df['f14']
C_cab = df['f15'] * 15.0
C_ent = df['f16']

# V7's highly successful penalties
C_ecl = df['f1'] * df['f11'] * 1.0 + (df['f3'] * 1000.0) + (df['f3'] * df['f1'] * 1.0)
C_retention = df['f2'] * 300.0

df['Profitability_Score'] = (
    R_interchange + R_interest + R_supp + R_credit_line
    - C_pts_cash - C_lounge - C_airline - C_cab - C_ent - C_ecl - C_retention
)

sub = df[['id', 'Profitability_Score']].rename(columns={'id': 'ID', 'Profitability_Score': 'Prediction'})
sub = sub.sort_values('ID').reset_index(drop=True)

xlsx_path = f'{OUT_DIR}/submission_v13_cash_basis_high_penalties.xlsx'
with pd.ExcelWriter(xlsx_path) as writer:
    sub.to_excel(writer, sheet_name='Predictions', index=False)
    df_framework.to_excel(writer, sheet_name='Profitability Framework', index=False)
print(f"Generated: {xlsx_path}")

