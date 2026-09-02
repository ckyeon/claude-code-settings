# 0040 — 기본 모델을 claude-fable-5-1[1m]으로, 해당 모델 effort는 high로

2026-09-02 `/model`·`/effort`로 변경한 값이 symlink를 통해 `user/shared/settings.json`에 반영됐다: `model`을 `claude-fable-5[1m]` → `claude-fable-5-1[1m]`으로, 전역 `effortLevel: xhigh`는 유지하되 `modelSettings.claude-fable-5-1.effortLevel: high`를 추가해 이 모델에서만 한 단계 낮췄다.
