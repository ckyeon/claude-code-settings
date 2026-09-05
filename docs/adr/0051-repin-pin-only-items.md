# 0051 — pin만 뒤처진 36개 항목을 upstream HEAD로 재pin, herdr는 제외

ADR 0050의 deep scan에서 tracked path에 변경이 없는 것으로 판정된 37개 중 36개를 재pin했다: mattpocock/skills 25개, claude-plugins-official 5개(plugin provenance), next.js template skill 4개, agent-browser `dogfood`, `fetch`. 콘텐츠 파일은 하나도 바뀌지 않고 sidecar 36개와 `SOURCES.md`만 바뀌었으므로, `copied` 항목까지 포함해 pin-only 판정이 맞았음을 확인했다. `herdr`는 ADR 0049에서 stable release commit에만 pin하기로 정했고 master HEAD는 release가 아니어서 의도적으로 제외했다.

## Consequences

- 이후 `check-updates`는 herdr 한 건만 outdated로 보고한다. herdr는 다음 stable release의 tag commit으로 재pin한다.
- sidecar 생성에 Python `glob("**", recursive=True)`를 쓰면 `.claude/` 같은 숨김 디렉터리를 건너뛰어 nextjs template 항목 5개가 빠진다. 이번엔 `os.walk`로 바꿔 36개를 맞췄다. `bin/` 도구는 이미 `os.walk` 기반이라 영향이 없다.
