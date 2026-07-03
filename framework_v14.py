import pandas as pd
import os

BASE = '/home/harshit/Documents/amex'
DATA_PATH = f'{BASE}/6a3eb196bc7a3_campus_challenge_r1_data.csv'
OUT_DIR = f'{BASE}/output'
TEMPLATE_PATH = f'{BASE}/6a3cb64c7cae4_campus_challenge_r1_submission_template.xlsx'

df = pd.read_csv(DATA_PATH)

# Read BOTH sheets from template to preserve exact format
xl = pd.ExcelFile(TEMPLATE_PATH)
print("Template sheets:", xl.sheet_names)
df_framework = pd.read_excel(TEMPLATE_PATH, sheet_name='Profitability Framework')
df_template_pred = pd.read_excel(TEMPLATE_PATH, sheet_name='Predictions')
print("Predictions columns:", list(df_template_pred.columns))
print("Profitability Framework columns:", list(df_framework.columns))

# Imputation
risk_median = df['f11'].median()
df['f11'] = df['f11'].fillna(risk_median)
for f in ['f6', 'f7', 'f8', 'f9', 'f10']:
    df[f] = df[f].fillna(0)
for f in ['f1', 'f2', 'f3', 'f4', 'f5', 'f12', 'f13', 'f14', 'f15',
          'f16', 'f17', 'f18', 'f19', 'f20', 'f21', 'f22', 'f23']:
    df[f] = df[f].fillna(0)

# === V14: V7 baseline + Amex 10-K grounded points WAC recalibration ===
# Change: pts_earned * 0.015 * 0.50 (V7) -> pts_earned * 0.007 * 0.96 (Amex 10-K)
# URR = 96% (from Amex 2023 10-K), WAC = 0.007 (0.7 cents per point, blended)

R_interchange = (df['f6'] + df['f9']) * 0.030 + (df['f7'] + df['f8'] + df['f10']) * 0.020
R_interest = df['f1'] * 0.24
R_supp = df['f19'] * 100.0 + df['f20'] * 100.0
R_credit_line = df['f17'] * 0.0001

pts_earned = df['f6'] * 5 + df['f9'] * 5 + df['f7'] * 1 + df['f8'] * 1 + df['f10'] * 1
# KEY CHANGE: WAC=0.007 (Amex 10-K), URR=0.96 (Amex 10-K) -> 0.00672 effective rate
C_pts_accrual = pts_earned * 0.007 * 0.96

C_lounge = df['f13'] * 40.0
C_airline = df['f14']
C_cab = df['f15'] * 15.0
C_ent = df['f16']

C_ecl = df['f1'] * df['f11'] * 1.0 + (df['f3'] * 1000.0) + (df['f3'] * df['f1'] * 1.0)
C_retention = df['f2'] * 300.0

df['Profitability_Score'] = (
    R_interchange + R_interest + R_supp + R_credit_line
    - C_pts_accrual - C_lounge - C_airline - C_cab - C_ent - C_ecl - C_retention
)

# Build Predictions sheet with EXACT column names from template
sub = df[['id', 'Profitability_Score']].copy()
sub = sub.rename(columns={'id': 'ID', 'Profitability_Score': 'Prediction'})
sub = sub.sort_values('ID').reset_index(drop=True)

print(f"\nPredictions shape: {sub.shape}")
print(f"Predictions columns: {list(sub.columns)}")
print(f"Sample:\n{sub.head(3)}")

# Write with EXACT sheet names matching template
xlsx_path = f'{OUT_DIR}/submission_v14_wac_recalibrated.xlsx'
with pd.ExcelWriter(xlsx_path, engine='openpyxl') as writer:
    sub.to_excel(writer, sheet_name='Predictions', index=False)
    df_framework.to_excel(writer, sheet_name='Profitability Framework', index=False)

# Verify the output
xl_out = pd.ExcelFile(xlsx_path)
print(f"\n=== VERIFICATION ===")
print(f"Output sheets: {xl_out.sheet_names}")
for sheet in xl_out.sheet_names:
    df_check = pd.read_excel(xlsx_path, sheet_name=sheet)
    print(f"  '{sheet}' -> columns: {list(df_check.columns)}, rows: {len(df_check)}")

print(f"\nGenerated: {xlsx_path}")
