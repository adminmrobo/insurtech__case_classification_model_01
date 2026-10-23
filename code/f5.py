"""
AI(인공지능) x 비즈니스 #1 인슈어테크_01_분류모델 · 5편 정식 코드 (f5.py)
글 · 안상선 ((주)M-Robo 대표) · CC BY-NC 4.0

하는 일
 ① 최종 모델(로지스틱 + 4편 임계값)의 판정을 '정답'으로 만든다 (실제 Claim 이 아님)
 ② 의사결정나무가 그 판정을 흉내 내게 학습한다 = 대리모델(surrogate)
 ③ 깊이 / 규칙 개수(max_leaf_nodes)에 따른 충실도(로지스틱과 일치율)를 잰다
 ④ 실제 정답으로 학습한 나무(3편)와 비교하고, 판정 기준서(조건문)를 출력한다
"""
import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.model_selection import StratifiedKFold, cross_val_predict, validation_curve
from sklearn.metrics import precision_recall_curve, recall_score, precision_score, confusion_matrix
import common

PATH = os.environ.get('TI_DATA', common.DATA_URL)
PASS = 0.95   # 충실도 합격선

raw, df, X, y, tr, te, info = common.load_all(PATH)
X_train, X_test, y_train, y_test = X.iloc[tr], X.iloc[te], y.iloc[tr], y.iloc[te]
scaler = StandardScaler().fit(X_train)
Xtr, Xte = scaler.transform(X_train), scaler.transform(X_test)
cv5 = StratifiedKFold(n_splits=5, shuffle=True, random_state=common.SEED)

# ① 선생님 모델 = 로지스틱 + 4편 임계값
lr = LogisticRegression(max_iter=1000, class_weight='balanced', random_state=common.SEED)
oof = cross_val_predict(lr, Xtr, y_train, cv=cv5, method='predict_proba')[:, 1]
p, r, t = precision_recall_curve(y_train, oof)
threshold = t[np.where(r[:-1] >= 0.80)[0][-1]]
lr.fit(Xtr, y_train)
teach_tr = (lr.predict_proba(Xtr)[:, 1] >= threshold).astype(int)
teach_te = (lr.predict_proba(Xte)[:, 1] >= threshold).astype(int)

# ② ③ 나무는 표준화 전 원래 단위로 학습 -> 규칙이 '일 · 금액' 단위로 나온다
Xtr_raw, Xte_raw = X_train.reset_index(drop=True), X_test.reset_index(drop=True)
rows = []
for d in range(2, 9):
    s = DecisionTreeClassifier(max_depth=d, random_state=common.SEED).fit(Xtr_raw, teach_tr)
    pr = s.predict(Xte_raw)
    rows.append({'max_depth': d, 'rules': s.get_n_leaves(), 'fidelity': (pr == teach_te).mean(), 'recall': recall_score(y_test, pr)})
print(pd.DataFrame(rows).round(4).to_string(index=False))

leaf_range = np.array([4, 6, 8, 10, 12, 14, 16, 20, 24, 32])
_, va = validation_curve(DecisionTreeClassifier(random_state=common.SEED), Xtr_raw, teach_tr, param_name='max_leaf_nodes',
                         param_range=leaf_range, cv=cv5, scoring='accuracy', n_jobs=-1)
cv_fid = va.mean(axis=1)
print('cv fidelity by rules:', dict(zip(leaf_range.tolist(), cv_fid.round(4).tolist())))
ok = cv_fid >= PASS
leaves = int(leaf_range[ok.argmax()]) if ok.any() else int(leaf_range[-1])
sur = DecisionTreeClassifier(max_leaf_nodes=leaves, random_state=common.SEED).fit(Xtr_raw, teach_tr)
y_sur = sur.predict(Xte_raw)

# ④ 비교: 실제 정답으로 학습한 나무(3편과 같은 설정)
dt = DecisionTreeClassifier(max_depth=6, class_weight='balanced', random_state=common.SEED).fit(Xtr, y_train)
y_dt = dt.predict(Xte)
cmp = []
for name, pr, rules in [('Tree (actual y)', y_dt, dt.get_n_leaves()), ('Logistic (teacher)', teach_te, None), ('Surrogate tree', y_sur, sur.get_n_leaves())]:
    tn, fp, fn, tp = confusion_matrix(y_test, pr).ravel()
    cmp.append({'model': name, 'recall': recall_score(y_test, pr), 'precision': precision_score(y_test, pr), 'accuracy': (tp + tn) / len(pr),
                'fidelity': (pr == teach_te).mean(), 'missed': fn, 'flagged': (tp + fp) / len(pr), 'rules': rules})
print(pd.DataFrame(cmp).round(4).to_string(index=False))
print(f"selected rules={leaves}  depth={sur.get_depth()}")
print(export_text(sur, feature_names=X.columns.tolist(), decimals=2))
