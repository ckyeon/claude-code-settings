---
name: herdr-fleet
description: herdr fleet, 곧 한 세션이 herdr agent 여럿을 함께 운영하는 절차. herdr agent를 셋 넘게 띄울 때 쓴다.
---

# herdr fleet

fleet은 한 세션이 띄워 함께 운영하는 herdr agent 묶음이고, fleet을 띄운 세션이 조정자다. agent 하나를 띄우고 다루는 명령은 `/herdr` skill을 따르고, 이 skill은 여럿을 함께 운영할 때 더할 장치만 담는다.

## 시작할 때

1. 조정자 scratchpad 아래에 `fleet/`을 만들고, 그 안에 `status/`, `drafts/`, `done/`을 만든다. 아래에서 `F`는 `fleet/`의 절대 경로다.
2. board를 만든다. board(`$F/board.md`)는 과제의 성공 기준에서 뽑은 풀어야 할 문제 목록이고, 문제마다 맡은 agent와 현황을 한 줄로 적는다. board는 조정자만 고친다.
3. 내보낼 산출물을 정한다. 내보낼 산출물은 fleet 밖으로 나가는 결과물이다. 사용자에게 건네는 문서, 서버가 서비스하는 파일, main branch가 그 예다.
   - 둘 이상의 agent 결과가 같은 내보낼 산출물로 모이면 검수 agent를 하나 둔다. 결과를 내는 agent는 자기 초안 자리에만 쓰고, 검수 agent가 들어오는 초안을 지켜보며 검수한다.
   - 결과를 내는 agent가 하나뿐이면 조정자가 검수한다.
   - 내보낼 산출물이 사용자 밖의 사람에게 바로 닿으면(고객이 쓰는 서버, 공개되는 문서 등) 과제에 적혀 있어도 내보낼 때마다 사용자 승인을 받는다. 조정자가 검수를 마친 내용이나 diff를 사용자에게 보이고, 승인을 받은 다음 내보낸다. 검수 agent는 내보낼 준비가 되면 그 내용을 요청 줄에 올리고 승인을 기다린다. 사용자의 repo 안에서 끝나는 내보내기는 과제가 정한 대로 한다.
4. 초안 자리를 정한다. 파일 초안의 자리는 `$F/drafts/<이름>/`이다. 코드 초안의 자리는 그 agent의 branch다. agent 여럿이 동시에 코드를 쓰면 agent마다 worktree가 있어야 한 agent의 checkout이 다른 agent의 작업 파일을 바꾸지 않는다. `/herdr` skill은 사용자가 요청할 때만 worktree를 만들므로, 사용자에게 agent마다 worktree를 만들지 묻는다.
   - 사용자가 원하면 agent마다 `herdr worktree create --branch <그 agent의 branch>`로 worktree를 만들고 그 안에서 agent를 띄운다.
   - 원하지 않으면 한 checkout의 작업 branch 하나에서 agent마다 고칠 파일을 겹치지 않게 나누고, 조정자가 agent마다 따로 commit한다.
5. 지시서마다 agent 이름, 결과를 쓸 곳, 상태 파일의 절대 경로 `$F/status/<이름>.md`, 아래 형식과 그 설명을 적는다. 그리고 "보고와 요청은 이 파일에만 쓰고, 상태가 바뀔 때마다 맨 위 네 줄을 고친다"고 적는다. 상태 파일 이름은 herdr agent 이름과 같게 한다.
6. § digest를 Monitor로 띄운다.

모든 agent에게 지시서를 보냈고 digest가 떠 있으면 시작이 끝난다.

상태 파일 맨 위 네 줄의 형식이다. 다섯째 줄부터는 자유롭게 쓴다.

```
진행: 진행 중 | 대기 | 끝남
맡은 일: <한 줄>
막힌 것: 없음 | <한 줄>
요청: 없음 | <조정자에게 바라는 것 한 줄, 예: reset>
```

다른 agent의 결과나 사용자 승인을 기다리는 동안은 "진행: 대기"로 쓴다. 그래야 digest가 기다리는 agent와 보고 없이 멈춘 agent를 구별한다.

## 상태 한 장

진척은 이 명령 하나로 본다. agent마다 herdr 상태, 상태 파일을 마지막으로 고친 시각, 맨 위 네 줄을 보여 준다.

```bash
F=<fleet 디렉터리>
herdr agent list | python3 -c '
import json, os, sys, time
d = os.path.join(sys.argv[1], "status")
st = {a["name"]: a["agent_status"] for a in json.load(sys.stdin)["result"]["agents"] if "name" in a}
for f in sorted(os.listdir(d)):
    p, n = os.path.join(d, f), f[:-3]
    print("== %s [%s] (%s)" % (n, st.get(n, "목록에 없음"), time.strftime("%H:%M", time.localtime(os.path.getmtime(p)))))
    print("\n".join(open(p).read().splitlines()[:4]))
' "$F"
```

시각이 오래된 agent는 상태 파일 대신 `herdr agent read <이름>`으로 지금 화면을 보고 판단한다.

## digest

digest는 조정자가 행동할 변화만 한 줄로 알리는 Monitor다. 다음 중 하나가 바뀔 때만 한 줄을 낸다.

- 상태 파일의 요청이나 막힘, 또는 "진행: 끝남"
- herdr 상태가 `blocked`인 agent
- herdr 상태는 `idle`이나 `done`인데 상태 파일은 "진행: 진행 중"인 agent. 보고 없이 멈춘 agent다.

```bash
F=<fleet 디렉터리>
prev=""
while true; do
  cur=$(herdr agent list 2>/dev/null | python3 -c '
import json, os, sys
d = os.path.join(sys.argv[1], "status")
try:
    st = {a["name"]: a["agent_status"] for a in json.load(sys.stdin)["result"]["agents"] if "name" in a}
except Exception:
    st = {}
out = []
for f in sorted(os.listdir(d)):
    n = f[:-3]
    head = open(os.path.join(d, f)).read().splitlines()[:4]
    out += [n + " " + l for l in head if l == "진행: 끝남" or (l.startswith(("막힌 것:", "요청:")) and not l.endswith(": 없음"))]
    if st.get(n) == "blocked":
        out.append(n + " herdr blocked")
    elif st.get(n) in ("idle", "done") and "진행: 진행 중" in head:
        out.append(n + " 보고 없이 멈춤")
print("; ".join(out))
' "$F")
  [ "$cur" != "$prev" ] && echo "fleet: ${cur:-요청, 막힘, 끝남, 멈춤 없음}"
  prev=$cur
  sleep 60
done
```

`timeout_ms`는 최대값인 1800000으로 둔다. 만료 알림이 오면 § 정기 보고를 한 다음 다시 띄운다.

알림을 받아 행동했으면 board의 해당 문제 현황도 고친다.

## 정기 보고

fleet이 도는 동안 digest가 만료될 때마다, 곧 30분마다 board를 고친 다음 그 내용으로 사용자에게 한 장으로 보고한다.

- 풀고 있는 문제별 현황
- 목표에 수치가 있으면 목표 대비 수치
- 놓치고 있을지 모르는 것 하나

## 닫기

결과를 받은 agent는 바로 `herdr pane close <pane_id>`로 닫고, 그 상태 파일을 `$F/done/`으로 옮긴다.
