# Claude Code 설정 관리

이 repo가 Claude Code 설정 가운데 무엇을 책임지는지 말할 때 쓰는 용어집이다. repo의 목적은 재현이다.

## Language

### 목적

**재현(reproduce)**:
새 기기에서 이 repo와 그 안의 문서만으로 같은 Claude Code 환경을 만드는 일. 어떤 항목을 제대로 관리하는지 가르는 기준이다.
_Avoid_: 이주, 백업

### 관리 수준

**소유(owned)**:
repo의 파일이 곧 기기에 적용되는 설정인 상태. repo를 고치면 설정이 바뀐다.
_Avoid_: 관리, 직접 관리

**선언(declared)**:
repo가 있어야 할 항목의 목록과 만드는 방법을 적어 두고, 실제 적용은 기기에서 사람이 하는 상태.
_Avoid_: 추적, 기록만, provenance-only

**범위 밖(out of scope)**:
repo가 저장하지도 점검하지도 않는 상태.
_Avoid_: 관리 안 함, 미관리

### 출처

**출처(provenance)**:
항목이 어느 upstream의 어느 시점에서 왔는지에 관한 사실. 관리 수준과는 별개의 축이어서, 소유한 항목과 선언한 항목 모두 출처가 있을 수도 없을 수도 있다.

**항목(item)**:
출처가 기록된 파일 하나 또는 폴더 하나. 출처를 따질 때의 단위다.
_Avoid_: 엔트리, 대상

**sidecar**:
항목 하나의 출처 기록. 그 항목이 거쳐 온 upstream 시점들이 순서대로 쌓인다.
_Avoid_: 메타데이터 파일, provenance 파일

**pin**:
출처가 있는 항목에 대해, 마지막으로 내용을 검토한 upstream의 시점. 항목의 source마다 가장 새 기록이 현재 pin이다. 기기에 설치된 version을 뜻하지 않는다.
_Avoid_: 설치 version, 현재 version

**비교 대상(comparison target)**:
항목의 pin이 뒤처졌는지 판단할 때 견주는 upstream의 시점이자, re-pin이 향하는 곳. 보통은 upstream HEAD이고, 항목에 따라 가장 새 release나 marketplace가 가리키는 시점이다.
_Avoid_: head, 최신 commit

**re-pin**:
출처가 있는 항목의 pin을 더 새로운 upstream 시점으로 옮기는 일. 내용을 복사해 온 항목이면 내용도 그 시점의 것으로 바뀐다.
_Avoid_: 재pin, 재adopt, 재동기화

**추적(track)**:
출처가 있는 항목의 upstream 경로를 pin과 비교해 지켜보는 일. 그 경로를 tracked path라고 부르며, 현재 pin이 가리키는 경로만 해당한다. 마지막 기록이 `self`인 항목은 upstream과 갈라선 것이라 추적하지 않는다.
_Avoid_: 목록에 올린다는 뜻으로 쓰는 추적
