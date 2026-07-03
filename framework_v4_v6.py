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

def generate_submission(name, APR, POINT_VAL, ECL_MULT, RETENTION, COLLECTION_BASE, COLLECTION_BAL_MULT):
    R_interchange = (df['f6'] + df['f9']) * 0.030 + (df['f7'] + df['f8'] + df['f10']) * 0.020
    R_interest = df['f1'] * APR
    R_supp = df['f19'] * 100.0 + df['f20'] * 100.0
    R_credit_line = df['f17'] * 0.0001
    
    C_pts = df['f21'] * POINT_VAL
    C_lounge = df['f13'] * 40.0
    C_airline = df['f14']
    C_cab = df['f15'] * 15.0
    C_ent = df['f16']
    
    # Collection cost is base penalty + a multiplier on their revolve balance (if they default, we lose the balance)
    C_ecl = df['f1'] * df['f11'] * ECL_MULT + (df['f3'] * COLLECTION_BASE) + (df['f3'] * df['f1'] * COLLECTION_BAL_MULT)
    
    C_retention = df['f2'] * RETENTION
    
    df['Profitability_Score'] = (
        R_interchange + R_interest + R_supp + R_credit_line
        - C_pts - C_lounge - C_airline - C_cab - C_ent - C_ecl - C_retention
    )
    
    sub = df[['id', 'Profitability_Score']].rename(columns={'id': 'ID', 'Profitability_Score': 'Prediction'})
    sub = sub.sort_values('ID').reset_index(drop=True)
    
    xlsx_path = f'{OUT_DIR}/submission_{name}.xlsx'
    with pd.ExcelWriter(xlsx_path) as writer:
        sub.to_excel(writer, sheet_name='Predictions', index=False)
        df_framework.to_excel(writer, sheet_name='Profitability Framework', index=False)
    print(f"Generated: {xlsx_path}")


# Variant 4: High Retention & Collection Penalty
# Amex loses full balance on collection (f3), and retention offers cost ~$300 in points
generate_submission('v4_high_penalties', 
                    APR=0.24, POINT_VAL=0.015, ECL_MULT=1.0, 
                    RETENTION=300.0, COLLECTION_BASE=1000.0, COLLECTION_BAL_MULT=1.0)

# Variant 5: Higher ECL Multiplier
# Exposure at default is usually higher than average balance, so ECL_MULT = 1.5
generate_submission('v5_high_ecl', 
                    APR=0.24, POINT_VAL=0.015, ECL_MULT=1.5, 
                    RETENTION=300.0, COLLECTION_BASE=1000.0, COLLECTION_BAL_MULT=1.0)

# Variant 6: Low Point Cost (1 cent per point internal cost)
generate_submission('v6_low_point_cost', 
                    APR=0.24, POINT_VAL=0.010, ECL_MULT=1.0, 
                    RETENTION=300.0, COLLECTION_BASE=1000.0, COLLECTION_BAL_MULT=1.0)

