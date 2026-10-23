# AI(인공지능) x 비즈니스 #1 인슈어테크_01_분류모델 · 3편 초보용 코드 (e3.py)
# 글 · 안상선 ((주)M-Robo 대표) · CC BY-NC 4.0
# 규칙: def · for · lambda · 들여쓰기 없음. 맨 위 [다이얼] 몇 줄만 바꿔 다시 실행하세요.

# [다이얼] KNN 이웃 수, 의사결정나무 깊이
K = 15
TREE_DEPTH = 6
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
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC, LinearSVC
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import recall_score, precision_score

# ③ 표준화: 학습 데이터로만 fit
scaler = StandardScaler().fit(X_train)
X_train_s = scaler.transform(X_train)
X_test_s = scaler.transform(X_test)

# ④ 모델 5개 (증강 없이 class_weight='balanced', KNN은 임계값 1/K)
knn = KNeighborsClassifier(n_neighbors=K).fit(X_train_s, y_train)
X_svc, X_rest, y_svc, y_rest = train_test_split(X_train_s, y_train, train_size=15000, stratify=y_train, random_state=42)
svc = SVC(kernel='rbf', class_weight='balanced', random_state=42).fit(X_svc, y_svc)
lsvm = LinearSVC(C=0.1, max_iter=5000, class_weight='balanced', random_state=42).fit(X_train_s, y_train)
lr = LogisticRegression(max_iter=1000, class_weight='balanced', random_state=42).fit(X_train_s, y_train)
dt = DecisionTreeClassifier(max_depth=TREE_DEPTH, class_weight='balanced', random_state=42).fit(X_train_s, y_train)

# ⑤ 시험 데이터 판정
p_knn = (knn.predict_proba(X_test_s)[:, 1] >= 1 / K).astype(int)
p_svc = svc.predict(X_test_s)
p_lsvm = lsvm.predict(X_test_s)
p_lr = lr.predict(X_test_s)
p_dt = dt.predict(X_test_s)

# ⑥ 재현율(실제 청구 중 맞힌 비율)과 정밀도, 기준선은 재현율 0
result = pd.DataFrame({'Model': ['KNN', 'SVC (RBF)', 'Linear SVM', 'Logistic', 'Decision Tree'], 'Recall': [recall_score(y_test, p_knn), recall_score(y_test, p_svc), recall_score(y_test, p_lsvm), recall_score(y_test, p_lr), recall_score(y_test, p_dt)], 'Precision': [precision_score(y_test, p_knn), precision_score(y_test, p_svc), precision_score(y_test, p_lsvm), precision_score(y_test, p_lr), precision_score(y_test, p_dt)]})
print(result.round(3))
