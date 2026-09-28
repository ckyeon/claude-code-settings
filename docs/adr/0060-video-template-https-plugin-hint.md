# 0060 — video template CLAUDE.md에 remotion 설치 HTTPS 우회법 추가

비디오 프로젝트로 복사되는 `project-templates/video/CLAUDE.md`의 Remotion 설치 안내에, `Host key verification failed`로 실패하면 `CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1`을 붙여 다시 실행하라는 한 줄을 넣었다. ADR 0059는 이 우회법을 settings repo 안의 plugin README에만 적어서, 다른 머신에서 template으로 프로젝트를 만든 사람은 볼 수 없었다.
