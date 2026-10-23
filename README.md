**[한국어](#ko)** · English · 中文 · 日本語 · O'zbekcha · Русский (번역 예정)

---
<a id="ko"></a>
# AI(인공지능) x 비즈니스 #1 인슈어테크_01_분류모델

보험사 보상 센터에 쌓인 여행자보험 가입 기록 63,326건으로, 보험금을 청구할 고객을 미리 가려내는 분류 모델을 만드는 인터랙티브 교재입니다. 버튼만 눌러 따라 하고, 같은 코드를 Google Colab에서 그대로 실행할 수 있습니다. 결측값·이상치 처리 → 모델 다섯 개 비교 → 임계값과 비용 → 최고 모델을 조건문으로 옮기는 대리모델 → 판정 앱까지 여섯 편입니다.

- 글: 글 · 안상선 ((주)M-Robo 대표)
- 라이선스: CC BY-NC 4.0 (코드·글·그림). 데이터는 원 출처의 조건을 따릅니다.
- 공개 주소: https://adminmrobo.github.io/ai-biz-insurtech-01/ (저장소 이름은 작가가 정함)

## 언어

| 언어 | 폴더 | 상태 |
|---|---|---|
| 한국어 | `/` | 원본 |
| English · 中文 · 日本語 · O'zbekcha · Русский | `en/` `zh/` `ja/` `uz/` `ru/` | 번역 예정 (캐릭터 그림을 넣은 뒤 한 번에) |

페이지 오른쪽 위 언어 상자로 고릅니다. 선택은 브라우저에 기억되고(`it1_lang`), 주소에 `?lang=xx`를 붙여도 됩니다. 아직 없는 언어판은 고르면 안내만 나오고 한국어판에 머뭅니다.

## 편 목록

| 편 | 파일 | 제목 | 유형 |
|---|---|---|---|
| 1 | `1_claim_question.html` | 청구는 1.5%: 정확도의 함정 | 해설형 · 확인 문제 4 |
| 2 | `2_data_cleaning.html` | 지우지 말고 고친다: 결측값과 이상치 | 방법형 · 확인 문제 3 |
| 3 | `3_five_models.html` | 모델 다섯, 경계 다섯 | 애니메이션형 · 확인 문제 4 · 가이드라인 |
| 4 | `4_threshold_lab.html` | 임계값과 비용 실험실 | 실험실형 · 확인 문제 3 · 실험 과제 4 |
| 5 | `5_surrogate_tree.html` | 최고 모델을 흉내 내는 나무 | 해설형 · 확인 문제 4 |
| 6 | `6_judge_app.html` | 기준서가 곧 판정: 청구 판정 앱 | 정리형 · 확인 문제 4 · 가이드라인 |

처음 화면 `index.html` · 교육자용 정답 `answers.html` (#a1 … #a6)

## 폴더

```
├── index.html                처음 화면 (식구 · 공통 소재 · 연구 지도 · 보는 법)
├── 1_claim_question.html … 6_judge_app.html
├── answers.html              교육자용 정답
├── 404.html                  GitHub Pages 용
├── code/                     정식 코드: common.py, f1.py ~ f6.py
│   └── easy/                 초보용 코드: e1.py ~ e6.py (def·for·lambda·들여쓰기 없음)
├── data/                     split.csv (학습/시험 나누기), surrogate_tree.json (6편 판정 규칙)
├── prompts/                  AI 튜터 프롬프트 ai_prompt_1.md ~ ai_prompt_6.md
├── README.md · LICENSE.md · .nojekyll
```

## 데이터

- **실제 공개 학습용 데이터**입니다(Travel Insurance, 63,326행 × 11열). 원본: https://raw.githubusercontent.com/fintech-data/Revolution/main/data/travel%20insurance.csv
- 이 시리즈는 **가상 데이터를 만들거나 데이터를 증강(SMOTE 등)하지 않습니다.** 불균형(청구 1.46%)은 `class_weight='balanced'`와 임계값으로 다룹니다.
- 열: Agency · Agency Type · Distribution Channel · Product Name · Duration · Destination · Net Sales · Commision (in value) · Gender · Age · Claim(맞힐 대상)
- 처리(2편, `code/common.py`의 `clean()`): Gender 결측 → Unknown · Duration ≤ 0 → 22(중앙값), > 731 → 731 · Age > 100 → 36(중앙값) · Net Sales 상·하위 0.1% → −112 ~ 399.6 · Commission 상위 0.1% → 186.71 · Destination 상위 10개국 + OTHER. 행은 지우지 않습니다.
- 나누기: 층화 80:20, `random_state=42` → 학습 50,660(청구 742) / 시험 12,666(청구 185). `data/split.csv`에 행 번호별로 기록.
- 기준선(“모두 청구 없음”): 시험 정확도 98.54%, 재현율 0%.
- 재현: `TI_DATA=<원본 csv 경로> python code/f1.py` … `f6.py` (경로를 주지 않으면 원본 주소에서 읽습니다).

## 주의

교육용 예시이며 보험 가입·보험료·보상에 대한 조언이 아닙니다. 실제 보험 심사와 보험료 산정은 감독 규정과 계리 기준을 따릅니다. 특정 집단에 불리한 특성(예: 성별·나이)의 사용은 금지되거나 제한될 수 있습니다.
