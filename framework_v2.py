import pandas as pd
import numpy as np
import os

BASE = '/home/harshit/Documents/amex'
DATA_PATH = f'{BASE}/6a3eb196bc7a3_campus_challenge_r1_data.csv'
OUT_DIR = f'{BASE}/output'
os.makedirs(OUT_DIR, exist_ok=True)

df = pd.read_csv(DATA_PATH)

# Imputation
risk_median = df['f11'].median()  # Use median instead of 75th percentile to not penalize missing risk too much
df['f11'] = df['f11'].fillna(risk_median)

for f in ['f6', 'f7', 'f8', 'f9', 'f10']:
    df[f] = df[f].fillna(0)

for f in ['f1', 'f2', 'f3', 'f4', 'f5', 'f12', 'f13', 'f14', 'f15',
          'f16', 'f17', 'f18', 'f19', 'f20', 'f21', 'f22', 'f23']:
    df[f] = df[f].fillna(0)

# Parameters
INTERCHANGE_RATE_PREMIUM= 0.030
INTERCHANGE_RATE_OTHER  = 0.020
APR_PROXY               = 0.20     # Slightly lower APR proxy
POINT_VALUE_CENTS       = 0.015    # 1.5 cents
LOUNGE_UNIT_COST        = 40.0
CAB_MONTH_COST          = 15.0
ECL_MULTIPLIER          = 1.00     # Removed the 1.2x penalty to be more balanced
COLLECTION_CALL_PENALTY = 300.0
RETENTION_CALL_COST     = 75.0
SUPP_ACCT_VALUE         = 100.0    # Reduced from 200
CHARGE_CARD_VALUE       = 100.0    # Reduced from 150

# Revenue
# f6: Airlines, f9: Lodging -> Premium
# f7: Other, f8: Ent, f10: Dining -> Other
R_interchange = (df['f6'] + df['f9']) * INTERCHANGE_RATE_PREMIUM + (df['f7'] + df['f8'] + df['f10']) * INTERCHANGE_RATE_OTHER
R_interest = df['f1'] * APR_PROXY
R_supp = df['f19'] * SUPP_ACCT_VALUE + df['f20'] * CHARGE_CARD_VALUE
R_credit_line = df['f17'] * 0.0001 # Very small proxy just as tie-breaker

# Costs
# Use only CASH BASIS for points (actual redemptions), drop accrual (double counting)
C_pts = df['f21'] * POINT_VALUE_CENTS
C_lounge = df['f13'] * LOUNGE_UNIT_COST
C_airline = df['f14']
C_cab = df['f15'] * CAB_MONTH_COST
C_ent = df['f16']
C_ecl = df['f1'] * df['f11'] * ECL_MULTIPLIER + df['f3'] * COLLECTION_CALL_PENALTY
C_retention = df['f2'] * RETENTION_CALL_COST

df['Profitability_Score'] = (
    R_interchange + R_interest + R_supp + R_credit_line
    - C_pts - C_lounge - C_airline - C_cab - C_ent - C_ecl - C_retention
)

submission = df[['id', 'Profitability_Score']].rename(columns={'Profitability_Score': 'prediction'})
submission = submission.sort_values('id').reset_index(drop=True)
submission.to_csv(f'{OUT_DIR}/submission_v2_cash_basis.csv', index=False)

# Variant 3: Accrual Basis for Points (Drop C_pts cash, use accrual)
pts_earned = df['f6'] * 5 + df['f9'] * 5 + df['f7'] * 1 + df['f8'] * 1 + df['f10'] * 1
C_pts_accrual = pts_earned * POINT_VALUE_CENTS * 0.40 # 40% redemption rate
df['Profitability_Score_V3'] = (
    R_interchange + R_interest + R_supp + R_credit_line
    - C_pts_accrual - C_lounge - C_airline - C_cab - C_ent - C_ecl - C_retention
)
submission_v3 = df[['id', 'Profitability_Score_V3']].rename(columns={'Profitability_Score_V3': 'prediction'})
submission_v3 = submission_v3.sort_values('id').reset_index(drop=True)
submission_v3.to_csv(f'{OUT_DIR}/submission_v3_accrual_basis.csv', index=False)

print("Generated V2 (Cash Basis) and V3 (Accrual Basis) submissions.")
