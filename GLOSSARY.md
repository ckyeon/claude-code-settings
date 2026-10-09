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

**pin**:
출처가 있는 항목에 대해, 마지막으로 내용을 검토한 upstream의 시점. 기기에 설치된 version을 뜻하지 않는다.
_Avoid_: 설치 version, 현재 version

**추적(track)**:
출처가 있는 항목을 upstream의 어느 시점과 비교할지 정하는 일.
_Avoid_: 목록에 올린다는 뜻으로 쓰는 추적
