"""
AI(인공지능) x 비즈니스 #1 인슈어테크_01_분류모델 · 공통 코드 (common.py)
글 · 안상선 ((주)M-Robo 대표) · CC BY-NC 4.0

하는 일
 ① 여행자보험 데이터 읽기 (공개 학습용 데이터, 63,326건)
 ② 결측값 · 이상치를 업무 기준으로 고치기 (2편)
 ③ 범주형 원-핫 인코딩, 종속변수 Claim -> 0/1
 ④ 미리 정한 학습/시험 나누기 (층화 80:20, random_state=42 -> data/split.csv 와 같음)
 ⑤ 기준선: "모두 청구 없음"으로만 답하기

원칙: 데이터 증강(SMOTE 등 합성 데이터 생성)은 쓰지 않는다. 원본 행만 쓴다.
"""
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

DATA_URL = "https://raw.githubusercontent.com/fintech-data/Revolution/main/data/travel%20insurance.csv"
SEED = 42

RENAME = {'Agency Type': 'Agency_Type', 'Distribution Channel': 'Distribution_Channel',
          'Product Name': 'Product_Name', 'Net Sales': 'Net_Sales',
          'Commision (in value)': 'Commision_in_value'}
NUM_COLS = ['Duration', 'Net_Sales', 'Commision_in_value', 'Age']
CAT_COLS = ['Agency', 'Agency_Type', 'Distribution_Channel', 'Product_Name', 'Destination', 'Gender']


def load_raw(path=DATA_URL):
    """① 원본 데이터 읽기 (열 이름의 공백·괄호를 밑줄로)."""
    return pd.read_csv(path).rename(columns=RENAME)


def clean(df):
    """② 결측값 · 이상치를 업무 기준으로 고친다. 행은 하나도 지우지 않는다.

    - Gender 결측(약 71%) -> 'Unknown' 범주
    - Duration 0 이하 -> 정상값(>0)의 중앙값, 731일(2년) 초과 -> 731
    - Age 100 초과(118세 984건 등) -> 정상 나이(<=100)의 중앙값
    - Net_Sales 상·하위 0.1%, Commision 상위 0.1% -> 경계값으로 고정(윈저라이징)
    - Destination 149개국 -> 상위 10개국 + OTHER
    """
    df = df.copy()
    df['Gender'] = df['Gender'].fillna('Unknown').replace('None', 'Unknown')
    dur_med = df.loc[df['Duration'] > 0, 'Duration'].median()
    df['Duration'] = df['Duration'].mask(df['Duration'] <= 0, dur_med).clip(upper=731)
    age_med = df.loc[df['Age'] <= 100, 'Age'].median()
    df['Age'] = df['Age'].mask(df['Age'] > 100, age_med)
    lo, hi = df['Net_Sales'].quantile(0.001), df['Net_Sales'].quantile(0.999)
    df['Net_Sales'] = df['Net_Sales'].clip(lo, hi)
    c_hi = df['Commision_in_value'].quantile(0.999)
    df['Commision_in_value'] = df['Commision_in_value'].clip(upper=c_hi)
    top10 = df['Destination'].value_counts().index[:10]
    df['Destination'] = df['Destination'].where(df['Destination'].isin(top10), 'OTHER')
    info = {'duration_median': dur_med, 'age_median': age_med, 'net_low': lo, 'net_high': hi,
            'comm_high': c_hi, 'top10_destinations': list(top10)}
    return df, info


def encode(df):
    """③ X(원-핫) 와 y(청구=1) 만들기."""
    y = (df['Claim'] == 'Yes').astype(int)
    X = pd.get_dummies(df.drop(columns='Claim'), drop_first=True, dtype=int)
    return X, y


def split_index(y):
    """④ 미리 정한 나누기: 행 번호 기준 층화 80:20 (data/split.csv 와 같은 결과)."""
    idx = np.arange(len(y))
    tr, te = train_test_split(idx, test_size=0.2, stratify=y, random_state=SEED)
    return tr, te   # 순서도 노트북의 train_test_split 결과와 같게 유지


def load_all(path=DATA_URL):
    """①~④ 한 번에: 정리된 df, X, y, 학습/시험 행 번호, 처리 정보."""
    raw = load_raw(path)
    df, info = clean(raw)
    X, y = encode(df)
    tr, te = split_index(y)
    return raw, df, X, y, tr, te, info


def baseline(y_true):
    """⑤ 기준선: 모두 '청구 없음'으로 답할 때의 정확도와 재현율."""
    acc = float((y_true == 0).mean())
    return {'accuracy': acc, 'recall': 0.0}
