# 0132 — 추천할 때 공식 문서가 안내하는 경로를 먼저 추천한다

`user/shared/CLAUDE.md` 1절 "Present options" 항목에 세 문장을 더했다. library, template, platform의 공식 문서가 안내하는 경로가 있으면 그 경로를 먼저 추천한다. 다른 경로는 문서의 경로가 이 자리에서 실패한다는 근거가 있을 때만 추천하고, 무엇이 실패했는지 적는다. 문서가 다루지 않는 부분은 쓰고 있는 template이나 도구의 기본값을 추천한다.

## 경위

- 다른 프로젝트의 세션이 inbox에 남긴 건의(ADR 0098)에서 왔다. template을 도입하는 grilling에서 Claude가 analytics 연결, 폰트, package manager 버전 세 곳에 공식 문서와 다른 방법을 추천했다.
- 사용자는 "웬만하면 공식문서가 유도하는대로 추천해줬으면 좋겠어"라고 했고, 모든 프로젝트에 적용할 선호라고 확인했다. 그 선호는 그 프로젝트의 memory에만 있어서 다른 프로젝트의 세션은 읽지 못했다.

## 결정

- **"Verify, don't recall"과 따로 둔다.** 그 항목은 사실을 어디서 확인하는지를 정하고, 이 항목은 여러 선택지 중 무엇을 먼저 추천하는지를 정한다.
- **건의 문안의 마지막 문장을 넓혔다.** 건의는 "recommend the template default"였는데, template을 쓰지 않는 작업에도 맞도록 "the default of the template or tool in use"로 썼다.
- 반영한 뒤 그 프로젝트의 memory를 지웠다. memory 자체가 반영되면 지운다고 적고 있었다.
