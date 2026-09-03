#!/usr/bin/env python3
"""로컬 오디오·영상 파일 → Gemini API 전사 텍스트.

  python3 transcribe.py <파일> [--out <경로>] [--anchors [초]] [--plain]

경로는 Gemini 하나뿐이다 — 키(GEMINI_TRANSCRIBE_API_KEY)가 없거나 API가 실패하면
그대로 오류로 끝난다. 폴백(Whisper 등)과 URL 다운로드는 이 스크립트 밖이다.

  --anchors [초]   문단마다 [H:MM:SS] 앵커를 단다(기본 60초). 이때만 word timestamp를
                   켠다 — 공식 문서가 "정확도를 소폭 저하시킬 수 있다"고 경고하는
                   옵션이라 앵커가 필요 없으면 끈 채로 둔다(기본).
  --out <경로>     파일로 저장(기존 파일은 덮어쓰지 않는다). 없으면 stdout.
  --plain          frontmatter 없이 본문만.

25분 초과 오디오는 ffmpeg로 청크 분할 후 순서대로 이어 붙인다(앵커 모드에서는
오프셋 합산). 영상 컨테이너(.mp4 .mkv .mov .webm 영상)는 ffmpeg로 오디오만 뽑는다.
GEMINI_TRANSCRIBE_API_KEY만 읽는다 — 범용 GEMINI_API_KEY는 다른 과금 프로젝트일 수
있어 읽지 않는다. 과금은 입력 토큰만(실측 46분 ≈ 0.14 USD, 2026-09-02).

원본: llm-wiki .claude/skills/intake/scripts/yt2raw.py의 Gemini 경로(2026-09-02
실측 검증본)에서 위키 계약(raw/ 저장·유일성·Whisper 폴백)을 떼어낸 독립 복제.
"""

import argparse
import bisect
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile
import time
from datetime import date

GEMINI_MODEL = "gemini-3.5-transcribe"
GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta"
CHUNK_SEC = 1500  # word timestamp 한도가 30분 — 여유를 두고 25분 청크
AUDIO_MIME = {".webm": "audio/webm", ".m4a": "audio/mp4", ".mp3": "audio/mp3",
              ".ogg": "audio/ogg", ".opus": "audio/ogg", ".aac": "audio/aac",
              ".wav": "audio/wav", ".flac": "audio/flac"}
VIDEO_SUFFIX = {".mp4", ".mkv", ".mov", ".avi", ".m4v"}


def die(msg: str) -> None:
    print(f"오류: {msg}", file=sys.stderr)
    sys.exit(1)


def log(msg: str) -> None:
    print(msg, file=sys.stderr)


# ---------- HTTP (curl) ----------

def _curl_json(curl_args: list[str], what: str) -> dict:
    r = subprocess.run(["curl", "-sS", "--fail-with-body", *curl_args],
                       capture_output=True, text=True)
    body = r.stdout.strip()
    if r.returncode != 0:
        raise RuntimeError(f"{what} 실패: {(body or r.stderr.strip())[-300:]}")
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        raise RuntimeError(f"{what} 응답이 JSON이 아니다: {body[:200]}")


def _retry_delay_s(msg: str) -> float | None:
    """429 응답 본문의 'retry in 14.33s' 지시 파싱 — 없으면 None(재시도 불가 오류). 순수 함수."""
    m = re.search(r"[Rr]etry in ([0-9.]+)s", msg)
    return float(m.group(1)) if m else None


def _retrying(call, label: str):
    """rate limit(재시도 지시가 있는 429)이면 지시만큼 대기 후 재시도, 최대 4회.
    무료 티어 TPM(10k/분)에서 25분 청크(~37.5k 토큰)는 대기가 정상 경로다.
    지시 없는 오류(과금 소진 등)는 즉시 올린다."""
    for attempt in range(5):
        try:
            return call()
        except RuntimeError as e:
            delay = _retry_delay_s(str(e))
            if delay is None or attempt == 4:
                raise
            wait = min(delay + 2, 120)
            log(f"  rate limit({label}) — {wait:.0f}초 대기 후 재시도 ({attempt + 1}/4)...")
            time.sleep(wait)


# ---------- Gemini Files API + interactions ----------

def _processing(f: dict) -> bool:
    return f.get("state", "ACTIVE") == "PROCESSING"


def _gemini_upload(path: pathlib.Path, mime: str, key: str) -> str:
    """Files API 업로드(multipart) → ACTIVE 대기 → uri."""
    auth = ["-H", f"x-goog-api-key: {key}"]
    endpoint = GEMINI_BASE.removesuffix("/v1beta") + "/upload/v1beta/files"
    data = _curl_json(["-X", "POST", endpoint, *auth,
                       "-F", f"file=@{path};type={mime}"], "Files API 업로드")
    f = data.get("file", data)
    uri, name = f.get("uri"), f.get("name")
    if not uri:
        raise RuntimeError(f"업로드 응답에 uri가 없다: {json.dumps(data)[:200]}")
    for _ in range(30):  # 오디오 처리 대기 — 통상 수 초
        if not _processing(f):
            break
        time.sleep(2)
        f = _curl_json([f"{GEMINI_BASE}/{name}", *auth], "Files API 상태 조회")
    if _processing(f):
        raise RuntimeError("업로드 파일이 60초 내에 ACTIVE가 되지 않았다")
    return uri


def _gemini_transcribe(uri: str, mime: str, key: str, timestamps: bool) -> dict:
    mode: dict = {"type": "verbatim"}
    if timestamps:
        mode["timestamp_granularities"] = ["word"]
    body = {"model": GEMINI_MODEL,
            "input": [{"type": "audio", "uri": uri, "mime_type": mime}],
            "generation_config": {"transcription_config": {"mode": mode}}}
    return _curl_json(["-X", "POST", f"{GEMINI_BASE}/interactions",
                       "-H", f"x-goog-api-key: {key}", "-H", "Content-Type: application/json",
                       "--max-time", "1800", "-d", json.dumps(body)], "Gemini 전사 요청")


# ---------- 응답 파싱 (순수 함수) ----------

def chunk_texts(data: dict) -> list[str]:
    """interactions 응답 → 본문 텍스트 목록(content[].text 순서 그대로)."""
    out = []
    for step in data.get("steps", []):
        for content in step.get("content", []):
            text = (content.get("text") or "").strip()
            if text:
                out.append(text)
    return out


def _offset_ms(s: str) -> int:
    return int(round(float(s.rstrip("s")) * 1000))


def _longest_nondecreasing_idx(vals: list[int]) -> list[int]:
    """최장 비감소 부분수열의 인덱스 — 시각 오프셋의 다수 추세만 남기고 이상치를
    (앞으로 튄 값·뒤로 처진 값 모두) 걸러낸다. 실측 2026-09-02: 초반 주석 2개가 앞으로
    튀자 '직전보다 작으면 무시' 규칙이 뒤따르는 정상 오프셋 19분치를 통째로 버렸다."""
    tails: list[int] = []
    tails_idx: list[int] = []
    prev = [-1] * len(vals)
    for i, v in enumerate(vals):
        k = bisect.bisect_right(tails, v)
        if k == len(tails):
            tails.append(v)
            tails_idx.append(i)
        else:
            tails[k] = v
            tails_idx[k] = i
        prev[i] = tails_idx[k - 1] if k else -1
    out: list[int] = []
    i = tails_idx[-1] if tails_idx else -1
    while i != -1:
        out.append(i)
        i = prev[i]
    return out[::-1]


def chunk_segs(data: dict, offset_ms: int = 0,
               max_ms: int = (CHUNK_SEC + 5) * 1000) -> list[tuple[int, str]]:
    """interactions 응답 → (시작 ms + 청크 오프셋, 텍스트 조각) 목록. 순수 함수.

    본문은 content[].text(정본)에서 취하고, word_info 주석은 start_index(UTF-8 바이트
    위치) → start_offset(시각) 지도로만 쓴다. 실측: 25분 청크에서 주석이 단어를 빠뜨리고
    오프셋이 튄다 — 주석에서 단어를 뽑으면 본문이 손실된다. 시각은 max_ms 초과를 버린 뒤
    최장 비감소 부분수열만 인정한다(무시된 구간의 텍스트는 직전 앵커에 붙는다)."""
    segs: list[tuple[int, str]] = []
    for step in data.get("steps", []):
        for content in step.get("content", []):
            text = content.get("text") or ""
            if not text.strip():
                continue
            raw = text.encode("utf-8")
            cands: list[tuple[int, int]] = []
            for ann in sorted(content.get("annotations", []), key=lambda a: a.get("start_index", 0)):
                if ann.get("type") != "word_info" or "start_offset" not in ann:
                    continue
                ms = _offset_ms(ann["start_offset"])
                if ms <= max_ms:
                    cands.append((ann.get("start_index", 0), ms))
            marks = [cands[i] for i in _longest_nondecreasing_idx([ms for _, ms in cands])]
            if not marks or marks[0][0] > 0:
                marks.insert(0, (0, marks[0][1] if marks else 0))
            bounds = [i for i, _ in marks] + [len(raw)]
            for (i, ms), j in zip(marks, bounds[1:]):
                piece = raw[i:j].decode("utf-8", errors="ignore").strip()
                if piece:
                    segs.append((offset_ms + ms, piece))
    return segs


def paras_from(segs: list[tuple[int, str]], para_sec: int) -> str:
    """(시작 ms, 텍스트) 목록을 [H:MM:SS] 앵커 문단으로 조립."""
    paras: list[str] = []
    buf: list[str] = []
    para_start_ms = 0
    for t, text in segs:
        if buf and t - para_start_ms >= para_sec * 1000:
            paras.append(_para(para_start_ms, buf))
            buf, para_start_ms = [], t
        elif not buf:
            para_start_ms = t
        buf.append(text)
    if buf:
        paras.append(_para(para_start_ms, buf))
    return "\n\n".join(paras)


def _para(start_ms: int, chunks: list[str]) -> str:
    s = start_ms // 1000
    stamp = f"[{s // 3600}:{s % 3600 // 60:02d}:{s % 60:02d}]"
    return f"{stamp} " + re.sub(r"\s+", " ", " ".join(chunks)).strip()


# ---------- 오디오 준비 ----------

def _duration_s(path: pathlib.Path) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        raise RuntimeError(f"ffprobe 길이 확인 실패: {r.stderr.strip()[-200:]}")


def _ensure_audio(src: pathlib.Path, td: str) -> pathlib.Path:
    """영상 컨테이너면 오디오만 AAC(.m4a)로 뽑는다. 오디오면 그대로."""
    if src.suffix.lower() not in VIDEO_SUFFIX:
        return src
    out = pathlib.Path(td) / "audio.m4a"
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(src), "-vn", "-c:a", "aac",
                        "-b:a", "128k", str(out)], capture_output=True, text=True)
    if r.returncode != 0 or not out.exists():
        raise RuntimeError(f"ffmpeg 오디오 추출 실패: {r.stderr.strip()[-200:]}")
    return out


def _split_audio(audio: pathlib.Path, td: str) -> list[pathlib.Path]:
    """CHUNK_SEC 초과 오디오를 -c copy로 분할. 경계 오차는 패킷 단위(수십 ms)."""
    if _duration_s(audio) <= CHUNK_SEC:
        return [audio]
    out = pathlib.Path(td) / f"chunk%03d{audio.suffix}"
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(audio), "-f", "segment",
                        "-segment_time", str(CHUNK_SEC), "-c", "copy", str(out)],
                       capture_output=True, text=True)
    chunks = sorted(pathlib.Path(td).glob(f"chunk*{audio.suffix}"))
    if r.returncode != 0 or not chunks:
        raise RuntimeError(f"ffmpeg 분할 실패: {r.stderr.strip()[-200:]}")
    return chunks


def _gemini_key() -> str:
    key = os.environ.get("GEMINI_TRANSCRIBE_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_TRANSCRIBE_API_KEY 미설정")
    return key


# ---------- 전사 ----------

def transcribe(src: pathlib.Path, anchors_sec: int | None,
               dump_dir: str | None = None) -> str:
    """파일 → 본문 문자열. anchors_sec가 None이면 timestamp 없이 청크 본문을 이어 붙인다.
    dump_dir은 개발용: 청크별 응답 JSON을 보존해 파서를 재전사 비용 없이 반복한다."""
    key = _gemini_key()
    with tempfile.TemporaryDirectory() as td:
        audio = _ensure_audio(src, td)
        mime = AUDIO_MIME.get(audio.suffix.lower(), "audio/mpeg")
        chunks = _split_audio(audio, td)
        segs: list[tuple[int, str]] = []
        texts: list[str] = []
        for i, chunk in enumerate(chunks):
            if len(chunks) > 1:
                log(f"  청크 {i + 1}/{len(chunks)} 전사 중...")
            uri = _retrying(lambda: _gemini_upload(chunk, mime, key), "업로드")
            data = _retrying(lambda: _gemini_transcribe(uri, mime, key, anchors_sec is not None), "전사")
            if dump_dir:
                (pathlib.Path(dump_dir) / f"{src.stem}-chunk{i}-response.json").write_text(
                    json.dumps(data, ensure_ascii=False), encoding="utf-8")
            if anchors_sec is not None:
                part = chunk_segs(data, offset_ms=i * CHUNK_SEC * 1000)
                segs.extend(part)
            else:
                part = chunk_texts(data)
                texts.extend(part)
            if not part:
                raise RuntimeError(f"청크 {i + 1} 응답에 전사 본문이 없다: "
                                   f"{json.dumps(data, ensure_ascii=False)[:200]}")
    if anchors_sec is not None:
        return paras_from(segs, anchors_sec)
    return "\n\n".join(texts)


def frontmatter(src: pathlib.Path, anchors_sec: int | None, duration_s: float | None) -> str:
    kind = f"Gemini API 전사 ({GEMINI_MODEL}, verbatim"
    kind += " + word timestamps)" if anchors_sec is not None else ")"
    note = "필러·더듬음 보존, 화자 표지 미사용(발언자 구분은 문맥)"
    if anchors_sec is not None:
        note += f", 문단은 {anchors_sec}초 단위 [H:MM:SS] 앵커"
    lines = ["---",
             f'title: "{src.stem}"',
             f'source: "{src.name}"',
             f"created: {date.today().isoformat()}",
             f"transcript: {kind} — transcribe.py. {note}"]
    if duration_s is not None:
        lines.append(f"duration_min: {int(duration_s // 60)}")
    lines += ["---", ""]
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", help="로컬 오디오·영상 파일")
    ap.add_argument("--out", help="저장 경로(기존 파일은 덮어쓰지 않음). 없으면 stdout")
    ap.add_argument("--anchors", nargs="?", const=60, type=int, metavar="SEC",
                    help="[H:MM:SS] 앵커 문단(기본 60초). 지정 시에만 word timestamp를 켠다")
    ap.add_argument("--plain", action="store_true", help="frontmatter 없이 본문만")
    args = ap.parse_args()

    src = pathlib.Path(args.file).expanduser()
    if not src.is_file():
        die(f"파일이 없다: {src}")
    dest = pathlib.Path(args.out).expanduser() if args.out else None
    if dest and dest.exists():
        die(f"{dest} 가 이미 있다 — 덮어쓰지 않는다.")
    try:
        _gemini_key()  # 작업 전에 확인
        duration = None
        try:
            duration = _duration_s(src)
        except RuntimeError as e:
            log(f"경고: {e}")
        log(f"Gemini API 전사 중 ({GEMINI_MODEL}"
            f"{'' if duration is None else f', {int(duration // 60)}분'} — 길이에 따라 수 분)...")
        body = transcribe(src, args.anchors)
    except RuntimeError as e:
        die(str(e))
    text = ("" if args.plain else frontmatter(src, args.anchors, duration)) + body + "\n"
    if dest:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding="utf-8")
        log(f"저장: {dest} | {len(body.split()):,} 단어")
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    main()
