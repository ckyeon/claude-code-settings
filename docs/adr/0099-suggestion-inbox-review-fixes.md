# 0099 — ADR 0098 리뷰에서 나온 수정

`f34f060` 이후의 변경, 곧 ADR 0098을 Standards와 Spec 두 축으로 리뷰하고 그 결과를 반영했다. 바뀐 정책은 하나로, 사용자가 `~/.claude` 아래를 고치라고 하면 고친 다음 건의로 기록하던 단계를 없앴다. 그 변경을 받아들이지 않으면 건의 파일만 지워지고 수정은 commit되지 않은 채 남았기 때문이다.

## 고친 것

- **처리 절차**: CLAUDE.md의 "Process suggestions"가 거절 이유를 말하게 하고, 다른 프로젝트 정보를 빼야 하는 범위를 ADR에서 commit 메시지와 설정 변경까지 넓혔다. ADR 0098에만 있던 내용이다.
- **테스트**: `tests/run.sh`가 이 repo의 SessionStart hook도 검사하고, 제목 검사도 확인한다. 번호 붙이기 검사는 같은 초에 실행될 때만 그 경로를 탔다. 이제는 다음 몇 초의 파일 이름을 미리 차지해 두고 실행해서 항상 그 경로를 탄다.
- **문서**:
  - ADR 0098의 요약을 세 문장으로 줄이고, 버린 선택지를 Considered Options로 옮겼다.
  - CLAUDE.md at-a-glance의 `.claude/hooks/` 항목에 SessionStart hook을 넣고, 처리 절차 첫머리에서 그 항목과 겹치던 설명을 뺐다.
  - GLOSSARY의 inbox 항목이 범위 밖인 근거를 CLAUDE.md § Scope 규칙 3의 기준인 "Claude가 쓰는 상태"로 바꿨다.
- **용어**: "출발 프로젝트"를 "보낸 프로젝트"로 풀어 썼다. ADR 0098의 "skill 폴더"는 SKILL.md에 맞춰 "skill 디렉터리"로 바꿨다.
- **skill description**: 본문 1단계와 겹치던 설정 파일 목록을 뺐다.
- **script**: 실행될 수 없는 마지막 `return 1`을 지웠다.

## 고치지 않은 것

- **inbox 위치를 script와 hook이 따로 정한다.** 두 파일 모두 자기 경로에서 `inbox/`를 구하고, hook은 `*.md`만 센다. 한쪽을 바꾸면 다른 쪽이 어긋날 수 있다. 하지만 이제 `tests/run.sh`가 script로 쓴 파일을 hook으로 세므로 어긋나면 테스트가 실패한다. 경로 계산 한 줄을 공유하려고 모듈을 만들지는 않았다.
- **`--target`과 본문 구성은 강제하지 않는다.** 대상을 모르는 건의도 있고, 관찰, 제안, 근거 구성은 skill의 template이 맡는다.
