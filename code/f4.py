"""
AI(인공지능) x 비즈니스 #1 인슈어테크_01_분류모델 · 4편 정식 코드 (f4.py)
글 · 안상선 ((주)M-Robo 대표) · CC BY-NC 4.0

하는 일
 ① 로지스틱(class_weight='balanced')의 학습 데이터 5-Fold 교차검증 확률을 구한다
 ② Recall >= 목표치(0.80)를 만족하는 가장 높은 임계값을 고른다 (시험 데이터는 쓰지 않음)
 ③ 시험 데이터에서 기본 임계값 0.5 와 고른 임계값을 비교한다
 ④ 비용 다이얼: 놓친 청구 1건 비용 vs 심사 1건 비용 (가상 단가) 으로 총비용을 비교한다
"""
import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import precision_recall_curve, confusion_matrix
import common

PATH = os.environ.get('TI_DATA', common.DATA_URL)
TARGET_RECALL = 0.80     # [다이얼] 목표 재현율
COST_MISS = 50           # [다이얼] 놓친 청구 1건 비용 (가상 단가)
COST_REVIEW = 1          # [다이얼] 추가 심사 1건 비용 (가상 단가)

raw, df, X, y, tr, te, info = common.load_all(PATH)
X_train, X_test, y_train, y_test = X.iloc[tr], X.iloc[te], y.iloc[tr], y.iloc[te]
scaler = StandardScaler().fit(X_train)
Xtr, Xte = scaler.transform(X_train), scaler.transform(X_test)

# ① 교차검증 확률
lr = LogisticRegression(max_iter=1000, class_weight='balanced', random_state=common.SEED)
cv5 = StratifiedKFold(n_splits=5, shuffle=True, random_state=common.SEED)
oof = cross_val_predict(lr, Xtr, y_train, cv=cv5, method='predict_proba')[:, 1]

# ② 임계값 고르기
prec, rec, thr = precision_recall_curve(y_train, oof)
i = np.where(rec[:-1] >= TARGET_RECALL)[0][-1]
threshold = thr[i]
print(f"threshold={threshold:.4f}  cv_recall={rec[i]:.3f}  cv_precision={prec[i]:.3f}")

# ③ 시험 데이터 비교
lr.fit(Xtr, y_train)
proba = lr.predict_proba(Xte)[:, 1]
rows = []
for name, t in [('default 0.5', 0.5), ('tuned', threshold)]:
    tn, fp, fn, tp = confusion_matrix(y_test, (proba >= t).astype(int)).ravel()
    cost = fn * COST_MISS + (tp + fp) * COST_REVIEW
    rows.append({'threshold': name, 'value': round(float(t), 4), 'tp': tp, 'fn': fn, 'fp': fp, 'tn': tn,
                 'recall': tp / (tp + fn), 'precision': tp / (tp + fp), 'flagged': (tp + fp) / len(y_test), 'cost': cost})
base_cost = int(y_test.sum()) * COST_MISS
rows.append({'threshold': 'baseline (review nobody)', 'value': None, 'tp': 0, 'fn': int(y_test.sum()), 'fp': 0,
             'tn': int((y_test == 0).sum()), 'recall': 0.0, 'precision': 0.0, 'flagged': 0.0, 'cost': base_cost})
print(pd.DataFrame(rows).round(3).to_string(index=False))

# 확률 상위 N명만 심사할 때 찾는 청구 수
order = np.argsort(-proba)
cum = np.cumsum(y_test.values[order])
for n in [100, 500, 1000, 2000, 3000]:
    print(f"top {n:>5} ({n / len(y_test):.1%}): claims found {cum[n - 1]:>3} ({cum[n - 1] / y_test.sum():.1%})")
