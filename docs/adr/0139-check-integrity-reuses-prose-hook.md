# 0139 — ADR 산문 검사는 산문 기호 hook의 판정을 그대로 쓴다

`bin/check-integrity`의 ADR 산문 검사가 자기 regex와 줄 판정을 버리고 `user/shared/hooks/flag-prose-symbols.py`의 `findings()`를 불러 쓴다. ADR 0138로 같은 기호를 찾는 코드가 두 곳에 생겼는데, 한쪽만 고치면 같은 글을 두 검사가 다르게 판정하게 된다.

## 결정

- 기준은 hook 파일에 둔다. hook은 `~/.claude/hooks/shared/`에서 혼자 돌아야 하므로 repo의 `lib/`를 import할 수 없다. `check-integrity`는 repo 구조를 이미 알고 있으므로 hook 파일을 직접 불러올 수 있다.
- `tests/run.sh`의 sandbox repo에 hook 파일을 복사한다. `check-integrity`가 이제 그 파일 없이는 돌지 않는다.
- 오류 문구는 그대로 둔다. 한 줄에 기호가 여럿이면 모두 적는다.

## Consequences

- ADR 판정에서 달라진 것은 하나다. 파일 첫 줄이 `---`이면 frontmatter로 보고 건너뛴다. 지금 ADR 가운데 그런 파일은 없다.
- ADR 0116이 더한 test 셋을 포함해 `tests/run.sh` 174개가 모두 통과했다. PATH의 `python3`를 3.9.6으로 두고 돌린 `check-integrity`도 깨끗했다.
