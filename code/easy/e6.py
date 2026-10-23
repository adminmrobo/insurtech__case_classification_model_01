# AI(인공지능) x 비즈니스 #1 인슈어테크_01_분류모델 · 6편 초보용 코드 (e6.py)
# 글 · 안상선 ((주)M-Robo 대표) · CC BY-NC 4.0
# 규칙: def · for · lambda · 들여쓰기 없음. 맨 위 [다이얼] 몇 줄만 바꿔 다시 실행하세요.

# [다이얼] 저장할 파일 이름
TREE_FILE = 'surrogate_tree.json'
TEST_FILE = 'app_test_data.csv'
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
import json
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import precision_recall_curve, confusion_matrix

# ③ 5편 대리모델 다시 만들기
scaler = StandardScaler().fit(X_train)
X_train_s = scaler.transform(X_train)
lr = LogisticRegression(max_iter=1000, class_weight='balanced', random_state=42)
oof = cross_val_predict(lr, X_train_s, y_train, cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=42), method='predict_proba')[:, 1]
pr_p, pr_r, pr_t = precision_recall_curve(y_train, oof)
threshold = pr_t[np.where(pr_r[:-1] >= 0.80)[0][-1]]
teacher_train = (lr.fit(X_train_s, y_train).predict_proba(X_train_s)[:, 1] >= threshold).astype(int)
surrogate = DecisionTreeClassifier(max_leaf_nodes=14, random_state=42).fit(X_train, teacher_train)

# ④ 나무 구조를 JSON 으로 저장 -> 판정 앱이 그대로 실행
share = surrogate.tree_.value[:, 0, :] / surrogate.tree_.value[:, 0, :].sum(axis=1, keepdims=True)
tree_export = {'feature_names': X.columns.tolist(), 'feature': surrogate.tree_.feature.tolist(), 'threshold': surrogate.tree_.threshold.tolist(), 'children_left': surrogate.tree_.children_left.tolist(), 'children_right': surrogate.tree_.children_right.tolist(), 'claim_share': share[:, 1].round(4).tolist(), 'n_samples': surrogate.tree_.n_node_samples.tolist()}
json.dump(tree_export, open(TREE_FILE, 'w'))

# ⑤ 앱 검증용 시험 데이터 (정답 + 노트북 판정) -> 앱에 올려 일치율 100% 확인
app_test = df.loc[X_test.index].copy()
app_test['Notebook_Surrogate_Pred'] = surrogate.predict(X_test)
app_test.to_csv(TEST_FILE, index=False)

# ⑥ 놓친 청구 칸 (실제 청구인데 저위험 판정)
tn, fp, fn, tp = confusion_matrix(y_test, app_test['Notebook_Surrogate_Pred']).ravel()
print('saved :', TREE_FILE, TEST_FILE, '| caught :', tp, '| missed :', fn, '| flagged :', round((tp + fp) / len(y_test), 3))
