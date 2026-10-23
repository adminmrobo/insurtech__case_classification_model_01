# AI(인공지능) x 비즈니스 #1 인슈어테크_01_분류모델 · 5편 초보용 코드 (e5.py)
# 글 · 안상선 ((주)M-Robo 대표) · CC BY-NC 4.0
# 규칙: def · for · lambda · 들여쓰기 없음. 맨 위 [다이얼] 몇 줄만 바꿔 다시 실행하세요.

# [다이얼] 대리모델 규칙 개수 (판정 기준서 한 장 = 10~16개)
MAX_RULES = 14
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
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import precision_recall_curve, recall_score

# ③ 선생님 모델 = 로지스틱 + 4편 임계값
scaler = StandardScaler().fit(X_train)
X_train_s = scaler.transform(X_train)
X_test_s = scaler.transform(X_test)
lr = LogisticRegression(max_iter=1000, class_weight='balanced', random_state=42)
oof = cross_val_predict(lr, X_train_s, y_train, cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=42), method='predict_proba')[:, 1]
pr_p, pr_r, pr_t = precision_recall_curve(y_train, oof)
threshold = pr_t[np.where(pr_r[:-1] >= 0.80)[0][-1]]
lr.fit(X_train_s, y_train)
teacher_train = (lr.predict_proba(X_train_s)[:, 1] >= threshold).astype(int)
teacher_test = (lr.predict_proba(X_test_s)[:, 1] >= threshold).astype(int)

# ④ 대리모델: 정답 자리에 '로지스틱의 판정'을 넣는다 (표준화 전 원래 단위)
surrogate = DecisionTreeClassifier(max_leaf_nodes=MAX_RULES, random_state=42).fit(X_train, teacher_train)
y_sur = surrogate.predict(X_test)

# ⑤ 충실도(로지스틱과 일치율)와 실제 재현율
print('rules :', surrogate.get_n_leaves(), '| fidelity :', round((y_sur == teacher_test).mean(), 4), '| recall :', round(recall_score(y_test, y_sur), 4))

# ⑥ 판정 기준서
print(export_text(surrogate, feature_names=X.columns.tolist(), decimals=2))
