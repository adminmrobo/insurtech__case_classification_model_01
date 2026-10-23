"""
AI(인공지능) x 비즈니스 #1 인슈어테크_01_분류모델 · 1편 정식 코드 (f1.py)
글 · 안상선 ((주)M-Robo 대표) · CC BY-NC 4.0

하는 일
 ① 데이터를 읽고 청구(Claim=Yes) 비율을 센다
 ② 기준선("모두 청구 없음")의 정확도와 재현율을 시험 데이터에서 잰다
 ③ 사람이 떠올릴 만한 간단한 규칙 3개를 같은 시험 데이터에서 잰다 -> 정확도의 함정
"""
import os
import pandas as pd
import common

PATH = os.environ.get('TI_DATA', common.DATA_URL)
raw, df, X, y, tr, te, info = common.load_all(PATH)

# ① 청구 비율
print(f"rows={len(df)}  claims={int(y.sum())}  claim_rate={y.mean():.4f}")
print(f"test rows={len(te)}  test claims={int(y.iloc[te].sum())}")

# ② 기준선
b = common.baseline(y.iloc[te])
print(f"baseline(all No): accuracy={b['accuracy']:.4f}  recall={b['recall']:.4f}")


# ③ 간단한 규칙 3개 (시험 데이터)
def score(pred, true):
    tp = int(((pred == 1) & (true == 1)).sum())
    fp = int(((pred == 1) & (true == 0)).sum())
    fn = int(((pred == 0) & (true == 1)).sum())
    tn = int(((pred == 0) & (true == 0)).sum())
    return {'acc': (tp + tn) / len(true), 'recall': tp / (tp + fn), 'precision': tp / max(tp + fp, 1),
            'flagged': (tp + fp) / len(true), 'tp': tp, 'fp': fp, 'fn': fn, 'tn': tn}


test = df.iloc[te]
yt = y.iloc[te].values
rules = {
    'Agency == C2B': (test['Agency'] == 'C2B').astype(int).values,
    'Net_Sales > 80': (test['Net_Sales'] > 80).astype(int).values,
    'Duration > 60': (test['Duration'] > 60).astype(int).values,
}
rows = [{'rule': name, **score(pred, yt)} for name, pred in rules.items()]
print(pd.DataFrame(rows).round(4).to_string(index=False))

# 판매점(Agency)별 청구율 상위 5
rate = df.groupby('Agency')['Claim'].apply(lambda s: (s == 'Yes').mean()).sort_values(ascending=False)
print((rate.head(5) * 100).round(2).to_string())
