# 0134 — transcribe 과금 설명에 출력 요금과 Tier 1 한도를 적는다

`transcribe` skill의 "실행 전 확인"에서 과금 줄을 고치고 한도 항목을 더했다. 과금은 입력과 출력을 합쳐 분당 약 0.005 USD로 적고, Tier 1 키에서 본 한도 두 개(분당 입력 10,000토큰, 하루 100건)를 적었다. `transcribe.py` docstring의 과금 문장도 같이 고쳤다.

## 경위

- 다른 프로젝트의 세션이 inbox에 남긴 건의(ADR 0098)에서 왔다. 그 세션은 오디오 1,421분을 돌렸는데, skill의 "입력 토큰만 과금, 분당 약 0.003 USD"로 어림하면 실제보다 약 40% 적게 나왔다.
- Google 요금 페이지를 직접 읽었다. `ai.google.dev/gemini-api/docs/pricing`은 지금 `aistudio.google.com/docs/pricing`으로 redirect된다. Gemini 3.5 Transcribe 절의 Paid Tier는 입력이 "$2.00 or $0.003/min", 출력이 "$12.00 or $0.002/min"이고, 각주가 "an effective blended rate of ~$0.005 per min for Transcribe"라고 적는다.

## 결정

- **2026-09-02의 "46분 실측 0.14 USD"는 뺐다.** 원래 기록은 "입력 토큰만 과금 실측 — 출력 토큰 0, 46분 ≈ $0.14"이다. 당시 응답의 출력 토큰이 0이었다는 관찰이라 지금 요금표와 맞지 않는다.
- **Tier 1 한도는 관찰값으로 적었다.** rate limit 페이지에는 Transcribe 한도가 없고, 한도는 AI Studio에서 보라고 한다. 두 값은 2026-11-23 429 응답 본문에서 왔다. 같은 페이지의 "Rate limits are applied per project, not per API key"와 "Requests per day (RPD) quotas reset at midnight Pacific time"도 함께 적었다.
- **"429로 거절된 요청은 하루 한도에 세지 않는다"는 넣지 않았다.** 건의 세션의 관찰이고, 문서로는 확인되지 않았다.
- "무료 티어는 분당 토큰 한도 때문에 대기가 생긴다"는 지금 키가 Tier 1이라 한도 항목으로 바꿨다. 실패한 뒤 다시 실행하라는 안내는 ADR 0133의 청크 캐시를 따른다.
