# AI(인공지능) x 비즈니스 #1 인슈어테크_01_분류모델 · 4편 초보용 코드 (e4.py)
# 글 · 안상선 ((주)M-Robo 대표) · CC BY-NC 4.0
# 규칙: def · for · lambda · 들여쓰기 없음. 맨 위 [다이얼] 몇 줄만 바꿔 다시 실행하세요.

# [다이얼] 목표 재현율, 놓친 청구 1건 비용, 심사 1건 비용 (가상 단가)
TARGET_RECALL = 0.80
COST_MISS = 50
COST_REVIEW = 1
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
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import precision_recall_curve, confusion_matrix

# ③ 표준화 + 학습 데이터 5-Fold 교차검증 확률 (시험 데이터는 임계값 고르는 데 쓰지 않음)
scaler = StandardScaler().fit(X_train)
X_train_s = scaler.transform(X_train)
X_test_s = scaler.transform(X_test)
lr = LogisticRegression(max_iter=1000, class_weight='balanced', random_state=42)
oof = cross_val_predict(lr, X_train_s, y_train, cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=42), method='predict_proba')[:, 1]

# ④ 목표 재현율을 만족하는 가장 높은 임계값
pr_p, pr_r, pr_t = precision_recall_curve(y_train, oof)
threshold = pr_t[np.where(pr_r[:-1] >= TARGET_RECALL)[0][-1]]
print('threshold :', round(threshold, 4))

# ⑤ 시험 데이터에 적용
proba = lr.fit(X_train_s, y_train).predict_proba(X_test_s)[:, 1]
tn, fp, fn, tp = confusion_matrix(y_test, (proba >= threshold).astype(int)).ravel()
print('caught :', tp, '| missed :', fn, '| extra reviews :', fp, '| recall :', round(tp / (tp + fn), 3))

# ⑥ 비용 비교: 아무도 심사 안 함(기준선) vs 이 임계값
print('cost baseline :', y_test.sum() * COST_MISS, '| cost model :', fn * COST_MISS + (tp + fp) * COST_REVIEW)
