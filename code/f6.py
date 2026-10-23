"""
AI(인공지능) x 비즈니스 #1 인슈어테크_01_분류모델 · 6편 정식 코드 (f6.py)
글 · 안상선 ((주)M-Robo 대표) · CC BY-NC 4.0

하는 일
 ① 5편의 대리모델 나무(규칙 14개)를 다시 만든다
 ② 나무 구조를 JSON 으로 내보낸다 -> 판정 앱이 이 조건문을 그대로 실행 (기준서 = 앱 코드)
 ③ JSON 만 보고 판정하는 함수를 따로 만들어, sklearn 판정과 100% 같은지 확인한다 (규칙 이식 검증)
 ④ 놓친 청구(실제 청구인데 저위험 판정) 칸을 따로 센다
"""
import os
import json
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import precision_recall_curve, confusion_matrix
import common

PATH = os.environ.get('TI_DATA', common.DATA_URL)
OUT = 'surrogate_tree.json'

# ① 대리모델 다시 만들기 (5편과 같은 설정)
raw, df, X, y, tr, te, info = common.load_all(PATH)
X_train, X_test, y_train, y_test = X.iloc[tr], X.iloc[te], y.iloc[tr], y.iloc[te]
scaler = StandardScaler().fit(X_train)
Xtr = scaler.transform(X_train)
cv5 = StratifiedKFold(n_splits=5, shuffle=True, random_state=common.SEED)
lr = LogisticRegression(max_iter=1000, class_weight='balanced', random_state=common.SEED)
oof = cross_val_predict(lr, Xtr, y_train, cv=cv5, method='predict_proba')[:, 1]
p, r, t = precision_recall_curve(y_train, oof)
threshold = t[np.where(r[:-1] >= 0.80)[0][-1]]
teach_tr = (lr.fit(Xtr, y_train).predict_proba(Xtr)[:, 1] >= threshold).astype(int)
sur = DecisionTreeClassifier(max_leaf_nodes=14, random_state=common.SEED).fit(X_train.reset_index(drop=True), teach_tr)

# ② JSON 내보내기
tree = sur.tree_
share = tree.value[:, 0, :] / tree.value[:, 0, :].sum(axis=1, keepdims=True)
export = {'feature_names': X.columns.tolist(), 'feature': tree.feature.tolist(), 'threshold': tree.threshold.tolist(),
          'children_left': tree.children_left.tolist(), 'children_right': tree.children_right.tolist(),
          'claim_share': share[:, 1].round(4).tolist(), 'n_samples': tree.n_node_samples.tolist(),
          'teacher_threshold': float(threshold), 'destinations': info['top10_destinations'] + ['OTHER']}
json.dump(export, open(OUT, 'w'))
print('saved', OUT, '| nodes', tree.node_count, '| rules', sur.get_n_leaves())


# ③ JSON 만 보고 판정 (앱과 같은 방식: x <= threshold 이면 왼쪽, float32 비교)
def judge(row, t=export):
    node = 0
    while t['children_left'][node] != -1:
        x = np.float32(row[t['feature'][node]])
        node = t['children_left'][node] if x <= t['threshold'][node] else t['children_right'][node]
    return int(t['claim_share'][node] > 0.5)


Xte_np = X_test.to_numpy()
app = np.array([judge(row) for row in Xte_np])
sk = sur.predict(X_test.reset_index(drop=True))
print(f"agreement JSON-judge vs sklearn: {(app == sk).mean():.4%}  ({int((app != sk).sum())} different)")

# ④ 놓친 청구 칸
tn, fp, fn, tp = confusion_matrix(y_test, app).ravel()
print(f"actual claims={tp + fn}  caught={tp}  missed={fn}  recall={tp / (tp + fn):.3f}  flagged={(tp + fp) / len(app):.3f}")
