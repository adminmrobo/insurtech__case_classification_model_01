"""
AI(인공지능) x 비즈니스 #1 인슈어테크_01_분류모델 · 2편 정식 코드 (f2.py)
글 · 안상선 ((주)M-Robo 대표) · CC BY-NC 4.0

하는 일
 ① 결측값 현황과 '결측 그룹'의 청구율을 확인한다
 ② 이상치를 IQR 기준과 업무 기준으로 각각 센다
 ③ 업무 기준으로 고친 뒤 전/후 통계를 비교한다 (행 삭제 없음)
"""
import os
import numpy as np
import pandas as pd
import common

PATH = os.environ.get('TI_DATA', common.DATA_URL)
raw = common.load_raw(PATH)

# ① 결측값
miss = raw.isnull().sum()
print(miss[miss > 0].to_string(), f"ratio={raw['Gender'].isnull().mean():.4f}")
g = raw['Gender'].fillna('Unknown')
rate = raw.groupby(g)['Claim'].apply(lambda s: (s == 'Yes').mean() * 100).round(2)
print('claim rate by Gender (%):', rate.to_dict())


# ② IQR 기준 이상치 개수 (가중치 1.5 / 3.0)
def iqr_count(s, w):
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    return int(((s < q1 - w * (q3 - q1)) | (s > q3 + w * (q3 - q1))).sum())


iqr = pd.DataFrame({w: {c: iqr_count(raw[c], w) for c in common.NUM_COLS} for w in [1.5, 3.0]})
print('IQR outliers:\n', iqr.to_string())

# ② 업무 기준
rules = {
    'Duration <= 0': int((raw['Duration'] <= 0).sum()),
    'Duration > 731': int((raw['Duration'] > 731).sum()),
    'Age > 100': int((raw['Age'] > 100).sum()),
    'Age == 118': int((raw['Age'] == 118).sum()),
    'Net_Sales < 0 (refund, keep)': int((raw['Net_Sales'] < 0).sum()),
    'Net_Sales outside 0.1%': int(((raw['Net_Sales'] < raw['Net_Sales'].quantile(0.001)) | (raw['Net_Sales'] > raw['Net_Sales'].quantile(0.999))).sum()),
    'Commission top 0.1%': int((raw['Commision_in_value'] > raw['Commision_in_value'].quantile(0.999)).sum()),
}
print('business rules:', rules)

# ③ 전/후 비교
df, info = common.clean(raw)
print({k: (round(float(v), 2) if not isinstance(v, list) else v) for k, v in info.items()})
cmp = pd.concat([raw[common.NUM_COLS].describe().T[['min', 'max', 'mean', 'std']].add_prefix('before_'),
                 df[common.NUM_COLS].describe().T[['min', 'max', 'mean', 'std']].add_prefix('after_')], axis=1)
print(cmp.round(2).to_string())
print('rows before/after:', len(raw), len(df))
