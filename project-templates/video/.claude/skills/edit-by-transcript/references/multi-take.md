# 여러 take에서 고르기

같은 내용을 여러 번 찍은 소스에서 부분(beat)마다 가장 좋은 take를 골라 잇는 일은 sub-agent 하나에 맡긴다. 아래 brief의 구조는 그대로 쓰고, 구성 예시는 재료에 맞게 바꾼다. sub-agent는 이 대화의 맥락을 모르므로 brief 안에 필요한 것을 모두 넣는다.

```
<영상 종류> 영상을 편집한다. 부분(beat)마다 가장 좋은 take를 골라, 소스 순서가 아니라 부분 순서로 이어라.

입력:
  - edit/takes_packed.md: 모든 take의 구절 단위 전사와 실측 무음 (절대 경로: <경로>)
  - 내용 맥락: <사용자에게 들은 2문장>
  - 화자: <이름, 역할, 말투>
  - 구성: <아래에서 고르거나 새로 정한 것>
  - 피할 말실수: <사전 점검 목록>
  - 목표 길이: <초>

구성 예시 (골라 쓰거나 새로 정한다):
  - 제품 소개: HOOK, PROBLEM, SOLUTION, BENEFIT, EXAMPLE, CTA
  - 튜토리얼: INTRO, SETUP, STEPS, GOTCHAS, RECAP
  - 인터뷰: QUESTION, ANSWER, FOLLOWUP 반복
  - 여행과 행사: ARRIVAL, HIGHLIGHTS, QUIET MOMENTS, DEPARTURE

규칙:
  - start와 end는 takes_packed.md의 "~ silence" 줄 범위 안에 둔다. 구절 안에서 잘라야 하면 그 경계를 "reason"에 "in-phrase"로 표시한다.
  - quote는 전사의 단어를 그대로 옮긴다.
  - 400ms 이상인 무음을 우선 컷 지점으로 쓴다.
  - 더 나은 take가 없는 말실수는 남기고 "reason"에 적는다.
  - 목표 길이를 넘으면 부분 하나를 빼거나 꼬리를 줄이고, 합계를 다시 계산한다.

출력 (JSON 배열만):
  [{"source": "C0103", "start": 2.42, "end": 6.85, "beat": "HOOK", "quote": "...", "reason": "..."}, ...]
마지막 줄에 총 길이를 한 줄로 적는다.
```

돌려받은 배열을 `edl.json`의 `ranges`에 넣은 다음, "in-phrase"로 표시된 경계는 SKILL.md 규칙 2대로 `timeline_view.py`로 확인해서 고친다.
