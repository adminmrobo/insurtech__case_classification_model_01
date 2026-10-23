# AI(인공지능) x 비즈니스 #1 인슈어테크_01_분류모델 · 2편 초보용 코드 (e2.py)
# 글 · 안상선 ((주)M-Robo 대표) · CC BY-NC 4.0
# 규칙: def · for · lambda · 들여쓰기 없음. 맨 위 [다이얼] 몇 줄만 바꿔 다시 실행하세요.

# [다이얼] IQR 가중치 (1.5 = 보통, 3.0 = 아주 먼 값만)
IQR_WEIGHT = 1.5
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

# ③ 원본을 다시 읽어 '고치기 전' 상태를 본다
raw = pd.read_csv(DATA_URL)
print('Gender missing :', raw['Gender'].isnull().sum(), '| ratio :', round(raw['Gender'].isnull().mean() * 100, 2), '%')

# ④ 결측 그룹의 청구율 (%) -> 결측 자체가 정보인지 확인
print((pd.crosstab(raw['Gender'].fillna('Unknown'), raw['Claim'], normalize='index')['Yes'] * 100).round(2))

# ⑤ IQR 기준 Age 이상치 개수
q1 = raw['Age'].quantile(0.25)
q3 = raw['Age'].quantile(0.75)
print('Age IQR outliers :', ((raw['Age'] < q1 - IQR_WEIGHT * (q3 - q1)) | (raw['Age'] > q3 + IQR_WEIGHT * (q3 - q1))).sum())

# ⑥ 업무 기준 이상치 개수
print('Duration <= 0 :', (raw['Duration'] <= 0).sum(), '| Duration > 731 :', (raw['Duration'] > 731).sum(), '| Age == 118 :', (raw['Age'] == 118).sum())

# ⑦ 고친 뒤(①에서 처리한 df) 전/후 비교
print(pd.concat([raw[['Duration', 'Age']].describe().T[['min', 'max', 'std']].add_prefix('before_'), df[['Duration', 'Age']].describe().T[['min', 'max', 'std']].add_prefix('after_')], axis=1).round(2))
