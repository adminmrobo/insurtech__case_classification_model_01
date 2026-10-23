"""
AI(인공지능) x 비즈니스 #1 인슈어테크_01_분류모델 · 3편 정식 코드 (f3.py)
글 · 안상선 ((주)M-Robo 대표) · CC BY-NC 4.0

하는 일
 ① 미리 정한 나누기 + 표준화(학습 데이터로만 fit)
 ② 모델 5개(KNN · SVC(RBF) · 선형 SVM · 로지스틱 · 의사결정나무)를 같은 데이터로 학습
    - 불균형은 데이터 증강 없이 class_weight='balanced' 로 보정
    - KNN 은 가중치 옵션이 없어 "이웃 15명 중 1명 이상 청구"를 위험으로 판정(임계값 1/15)
 ③ 시험 데이터에서 Accuracy · Precision · Recall · F1 · ROC-AUC 를 기준선과 함께 출력
"""
import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC, LinearSVC
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
import common

PATH = os.environ.get('TI_DATA', common.DATA_URL)
raw, df, X, y, tr, te, info = common.load_all(PATH)

# ① 나누기 + 표준화
X_train, X_test, y_train, y_test = X.iloc[tr], X.iloc[te], y.iloc[tr], y.iloc[te]
scaler = StandardScaler().fit(X_train)
Xtr = pd.DataFrame(scaler.transform(X_train), columns=X.columns)
Xte = pd.DataFrame(scaler.transform(X_test), columns=X.columns)

# ② 모델 5개
knn = KNeighborsClassifier(n_neighbors=15).fit(Xtr, y_train)
X_svc, _, y_svc, _ = train_test_split(Xtr, y_train, train_size=15000, stratify=y_train, random_state=common.SEED)
svc = SVC(kernel='rbf', C=1.0, gamma='scale', class_weight='balanced', random_state=common.SEED).fit(X_svc, y_svc)
lsvm = LinearSVC(C=0.1, max_iter=5000, class_weight='balanced', random_state=common.SEED).fit(Xtr, y_train)
lr = LogisticRegression(max_iter=1000, class_weight='balanced', random_state=common.SEED).fit(Xtr, y_train)
dt = DecisionTreeClassifier(max_depth=6, class_weight='balanced', random_state=common.SEED).fit(Xtr, y_train)

scores = {
    'KNN': knn.predict_proba(Xte)[:, 1],
    'SVC (RBF)': svc.decision_function(Xte),
    'Linear SVM': lsvm.decision_function(Xte),
    'Logistic': lr.predict_proba(Xte)[:, 1],
    'Decision Tree': dt.predict_proba(Xte)[:, 1],
}
preds = {
    'KNN': (scores['KNN'] >= 1 / 15).astype(int),
    'SVC (RBF)': svc.predict(Xte),
    'Linear SVM': lsvm.predict(Xte),
    'Logistic': lr.predict(Xte),
    'Decision Tree': dt.predict(Xte),
}

# ③ 결과표 (+ 기준선)
rows = [{'model': 'Baseline (all No)', 'accuracy': (y_test == 0).mean(), 'precision': 0.0, 'recall': 0.0, 'f1': 0.0,
         'roc_auc': 0.5, 'caught': 0, 'missed': int(y_test.sum())}]
for name in preds:
    p = preds[name]
    rows.append({'model': name, 'accuracy': accuracy_score(y_test, p), 'precision': precision_score(y_test, p),
                 'recall': recall_score(y_test, p), 'f1': f1_score(y_test, p), 'roc_auc': roc_auc_score(y_test, scores[name]),
                 'caught': int(p[y_test.values == 1].sum()), 'missed': int(y_test.sum() - p[y_test.values == 1].sum())})
print(pd.DataFrame(rows).round(3).to_string(index=False))
print('SVC support vectors:', int(svc.n_support_.sum()), '/ 15000')
