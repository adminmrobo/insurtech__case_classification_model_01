# AI(인공지능) x 비즈니스 #1 인슈어테크_01_분류모델 · 1편 초보용 코드 (e1.py)
# 글 · 안상선 ((주)M-Robo 대표) · CC BY-NC 4.0
# 규칙: def · for · lambda · 들여쓰기 없음. 맨 위 [다이얼] 몇 줄만 바꿔 다시 실행하세요.

# [다이얼] 사람이 떠올린 규칙: 이 판매점이면 '청구'로 답한다
RULE_AGENCY = 'C2B'
DATA_URL = 'https://raw.githubusercontent.com/fintech-data/Revolution/main/data/travel%20insurance.csv'

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

# ① 데이터 읽기 + 2편의 정리 규칙 (행 삭제 없음, 데이터 증강 없음)
df = pd.read_csv(DATA_URL)
df = df.rename(columns={'Agency Type': 'Agency_Type', 'Distribution Channel': 'Distribution_Channel', 'Product Name': 'Product_Name', 'Net Sales': 'Net_Sales', 'Commision (in value)': 'Commision_in_value'})
df['Gender'] = df['Gender'].fillna('Unknown')
df['Duration'] = df['Duration'].mask(df['Duration'] <= 0, df.loc[df['Duration'] > 0, 'Duration'].median()).clip(upper=731)
df['Age'] = df['Age'].mask(df['Age'] > 100, df.loc[df['Age'] <= 100, 'Age'].median())
df['Net_Sales'] = df['Net_Sales'].clip(df['Net_Sales'].quantile(0.001), df['Net_Sales'].quantile(0.999))
df['Commision_in_value'] = df['Commision_in_value'].clip(upper=df['Commision_in_value'].quantile(0.999))
top10 = df['Destination'].value_counts().index[:10]
df['Destination'] = df['Destination'].where(df['Destination'].isin(top10), 'OTHER')

# ② 인코딩 + 미리 정한 나누기 (층화 80:20, random_state=42)
y = (df['Claim'] == 'Yes').astype(int)
X = pd.get_dummies(df.drop(columns='Claim'), drop_first=True, dtype=int)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

# ③ 청구 비율 -> 아주 드문 사건 (불균형 데이터)
print('rows :', len(df), '| claims :', y.sum(), '| claim rate :', round(y.mean() * 100, 2), '%')

# ④ 기준선: 시험 데이터 전부 '청구 없음'으로 답하기
print('Baseline accuracy :', round((y_test == 0).mean(), 4), '| Baseline recall : 0.0')

# ⑤ 규칙 하나로 답하기: 판매점이 RULE_AGENCY 이면 청구(1)
rule_pred = (df.loc[X_test.index, 'Agency'] == RULE_AGENCY).astype(int)
tp = ((rule_pred == 1) & (y_test == 1)).sum()
print('Rule accuracy :', round((rule_pred == y_test).mean(), 4), '| Rule recall :', round(tp / y_test.sum(), 4), '| flagged :', round(rule_pred.mean(), 4))

# ⑥ 판매점별 청구율 상위 5 (%)
print((pd.crosstab(df['Agency'], df['Claim'], normalize='index')['Yes'] * 100).round(2).sort_values(ascending=False).head(5))
