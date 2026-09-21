#!/usr/bin/env python3
"""로컬 오디오·영상 파일 → Gemini API 전사 텍스트.

  python3 transcribe.py <파일> [--out <경로>] [--anchors [초]] [--speakers] [--smart]
                       [--lang <코드>] [--vocab <용어,...>] [--vocab-file <경로>] [--plain]

경로는 Gemini 하나뿐이다 — 키(GEMINI_TRANSCRIBE_API_KEY)가 없거나 API가 실패하면
그대로 오류로 끝난다. 폴백(Whisper 등)과 URL 다운로드는 이 스크립트 밖이다.

  --anchors [초]   문단마다 [H:MM:SS] 앵커를 단다(기본 60초). 이때만 word timestamp를
                   켠다 — 공식 문서가 "정확도를 소폭 저하시킬 수 있다"고 경고하는
                   옵션이라 앵커가 필요 없으면 끈 채로 둔다(기본).
  --speakers       화자를 구분해 발언 차례마다 "**spk_0:** 본문" 문단을 만든다. label은
                   익명이고 최대 8명이며, 3명 이상은 API가 실험적 기능으로 분류한다.
                   화자 정보는 word 주석에만 실려 오므로 word timestamp도 함께 켜진다.
                   25분 초과 파일은 청크마다 label을 새로 매기므로 c1-, c2- 접두어가 붙는다.
  --smart          verbatim 대신 smart mode. 필러와 반복을 지우고 목록과 날짜 형식을 정리한다.
  --lang <코드>    BCP-47 언어 코드, 쉼표로 여러 개(ko-KR,en-US). 없으면 자동 감지.
  --vocab <용어>   인식을 보정할 고유명사와 도메인 용어, 쉼표로 구분. 최대 1,000개이고
                   100개 안팎이 권장치다.
  --vocab-file <경로>  한 줄에 한 용어. --vocab과 합친다.
  --out <경로>     파일로 저장(기존 파일은 덮어쓰지 않는다). 없으면 stdout.
  --plain          frontmatter 없이 본문만.

API가 함께 받지 않는 조합은 요청 전에 오류로 끝난다: --smart는 --anchors, --speakers와
함께 쓸 수 없고, --vocab과 --vocab-file도 --anchors, --speakers와 함께 쓸 수 없다.

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
VOCAB_MAX = 1000  # custom_vocabulary 상한(공식 문서)
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


def transcription_config(anchors: bool, speakers: bool, smart: bool,
                         langs: list[str], vocab: list[str]) -> dict:
    """CLI 선택 → 요청의 transcription_config. 순수 함수.
    실측 2026-09-21: diarization_mode만 켜면 word_info 주석이 아예 오지 않아 화자 정보를
    읽을 곳이 없다. 그래서 speakers도 word timestamp를 함께 켠다."""
    mode: dict | str = "smart"
    if not smart:
        mode = {"type": "verbatim"}
        if speakers:
            mode["diarization_mode"] = "speaker"
        if anchors or speakers:
            mode["timestamp_granularities"] = ["word"]
    cfg: dict = {"mode": mode}
    if langs:
        cfg["language_codes"] = langs
    if vocab:
        cfg["custom_vocabulary"] = vocab
    return cfg


def _gemini_transcribe(uri: str, mime: str, key: str, tcfg: dict) -> dict:
    body = {"model": GEMINI_MODEL,
            "input": [{"type": "audio", "uri": uri, "mime_type": mime}],
            "generation_config": {"transcription_config": tcfg}}
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


Seg = tuple[int, str | None, str]  # (시작 ms, 화자 label 또는 None, 텍스트 조각)


def chunk_segs(data: dict, offset_ms: int = 0,
               max_ms: int = (CHUNK_SEC + 5) * 1000, spk_prefix: str = "") -> list[Seg]:
    """interactions 응답 → (시작 ms + 청크 오프셋, 화자, 텍스트 조각) 목록. 순수 함수.

    본문은 content[].text(정본)에서 취하고, word_info 주석은 start_index(UTF-8 바이트
    위치) → start_offset(시각)과 speaker 지도로만 쓴다. 실측: 25분 청크에서 주석이 단어를
    빠뜨리고 오프셋이 튄다 — 주석에서 단어를 뽑으면 본문이 손실된다. 시각은 max_ms 초과를
    버린 뒤 최장 비감소 부분수열만 인정한다(무시된 구간의 텍스트는 직전 앵커에 붙는다).

    자르는 지점은 인정된 시각 주석, 그리고 speaker가 직전과 달라지는 주석이다. 시각이
    무시된 주석에서 화자가 바뀌면 직전 시각을 물려받는다. speaker가 없는 응답(화자 구분
    off)에서는 시각 주석에서만 잘린다. label은 API의 "spk:0"을 "spk_0"으로 바꿔 쓴다 —
    문단 표지 "**label:**"에서 쌍점이 겹치지 않게 하기 위해서다."""
    segs: list[Seg] = []
    for step in data.get("steps", []):
        for content in step.get("content", []):
            text = content.get("text") or ""
            if not text.strip():
                continue
            raw = text.encode("utf-8")
            anns = [a for a in sorted(content.get("annotations", []),
                                      key=lambda a: a.get("start_index", 0))
                    if a.get("type") == "word_info"]
            timed: list[tuple[int, int]] = []  # (anns 인덱스, ms)
            for k, ann in enumerate(anns):
                if "start_offset" not in ann:
                    continue
                ms = _offset_ms(ann["start_offset"])
                if ms <= max_ms:
                    timed.append((k, ms))
            valid = dict(timed[i] for i in _longest_nondecreasing_idx([ms for _, ms in timed]))
            marks: list[tuple[int, int | None, str | None]] = []
            cur_ms: int | None = None
            cur_spk: str | None = None
            for k, ann in enumerate(anns):
                spk = ann.get("speaker", cur_spk)
                if k not in valid and spk == cur_spk:
                    continue
                cur_ms, cur_spk = valid.get(k, cur_ms), spk
                marks.append((ann.get("start_index", 0), cur_ms, cur_spk))
            first_ms = next((ms for _, ms, _ in marks if ms is not None), 0)
            if not marks or marks[0][0] > 0:
                marks.insert(0, (0, first_ms, marks[0][2] if marks else None))
            bounds = [i for i, _, _ in marks] + [len(raw)]
            for (i, ms, spk), j in zip(marks, bounds[1:]):
                piece = raw[i:j].decode("utf-8", errors="ignore").strip()
                if piece:
                    label = None if spk is None else spk_prefix + spk.replace(":", "_")
                    segs.append((offset_ms + (first_ms if ms is None else ms), label, piece))
    return segs


def paras_from(segs: list[Seg], para_sec: int | None) -> str:
    """조각 목록을 문단으로 조립. 화자가 바뀌면 새 문단이고, para_sec가 있으면 그 간격으로도
    나누며 [H:MM:SS] 앵커를 단다. para_sec가 None이면(화자 구분만) 앵커 없이 화자로만 나눈다."""
    paras: list[str] = []
    buf: list[str] = []
    para_start_ms = 0
    para_spk: str | None = None
    for t, spk, text in segs:
        if buf and (spk != para_spk
                    or (para_sec is not None and t - para_start_ms >= para_sec * 1000)):
            paras.append(_para(para_start_ms, buf, para_spk, para_sec is not None))
            buf = []
        if not buf:
            para_start_ms, para_spk = t, spk
        buf.append(text)
    if buf:
        paras.append(_para(para_start_ms, buf, para_spk, para_sec is not None))
    return "\n\n".join(paras)


def _para(start_ms: int, chunks: list[str], spk: str | None = None, stamp: bool = True) -> str:
    s = start_ms // 1000
    head = f"[{s // 3600}:{s % 3600 // 60:02d}:{s % 60:02d}] " if stamp else ""
    if spk is not None:
        head += f"**{spk}:** "
    return head + re.sub(r"\s+", " ", " ".join(chunks)).strip()


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


def _split_terms(s: str, sep: str) -> list[str]:
    return [t.strip() for t in s.split(sep) if t.strip()]


def _gemini_key() -> str:
    key = os.environ.get("GEMINI_TRANSCRIBE_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_TRANSCRIBE_API_KEY 미설정")
    return key


# ---------- 전사 ----------

def transcribe(src: pathlib.Path, anchors_sec: int | None, tcfg: dict,
               speakers: bool = False, dump_dir: str | None = None) -> str:
    """파일 → 본문 문자열. 앵커도 화자 구분도 없으면 청크 본문을 그대로 이어 붙인다.
    화자 label은 요청마다 등장 순서로 새로 매겨진다(실측 2026-09-21: 같은 두 목소리의
    순서를 뒤집은 클립에서 먼저 말한 쪽이 spk:0이 됐다). 그래서 청크가 둘 이상이면
    label에 c1-, c2- 접두어를 붙여 서로 다른 번호 체계임을 드러낸다.
    dump_dir은 개발용: 청크별 응답 JSON을 보존해 파서를 재전사 비용 없이 반복한다."""
    key = _gemini_key()
    use_segs = anchors_sec is not None or speakers
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
            data = _retrying(lambda: _gemini_transcribe(uri, mime, key, tcfg), "전사")
            if dump_dir:
                (pathlib.Path(dump_dir) / f"{src.stem}-chunk{i}-response.json").write_text(
                    json.dumps(data, ensure_ascii=False), encoding="utf-8")
            if use_segs:
                part = chunk_segs(data, offset_ms=i * CHUNK_SEC * 1000,
                                  spk_prefix=f"c{i + 1}-" if len(chunks) > 1 else "")
                segs.extend(part)
            else:
                part = chunk_texts(data)
                texts.extend(part)
            if not part:
                raise RuntimeError(f"청크 {i + 1} 응답에 전사 본문이 없다: "
                                   f"{json.dumps(data, ensure_ascii=False)[:200]}")
    if use_segs:
        return paras_from(segs, anchors_sec)
    return "\n\n".join(texts)


def frontmatter(src: pathlib.Path, anchors_sec: int | None, duration_s: float | None,
                tcfg: dict, speakers: bool = False) -> str:
    smart = tcfg["mode"] == "smart"
    opts = ["smart" if smart else "verbatim"]
    if anchors_sec is not None or speakers:
        opts.append("word timestamps")
    if speakers:
        opts.append("speaker diarization")
    if tcfg.get("language_codes"):
        opts.append("lang " + ",".join(tcfg["language_codes"]))
    if tcfg.get("custom_vocabulary"):
        opts.append(f"vocabulary {len(tcfg['custom_vocabulary'])}개")
    kind = f"Gemini API 전사 ({GEMINI_MODEL}, {' + '.join(opts)})"
    note = "필러와 반복 제거, 형식 정리" if smart else "필러·더듬음 보존"
    if speakers:
        note += ", 화자 label은 익명(spk_N)"
        if duration_s is not None and duration_s > CHUNK_SEC:
            note += f"이고 {CHUNK_SEC // 60}분 청크마다 새로 매긴다(c1-, c2- 접두어는 서로 다른 번호 체계)"
    else:
        note += ", 화자 표지 미사용(발언자 구분은 문맥)"
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
    ap.add_argument("--speakers", action="store_true",
                    help="화자 구분. 발언 차례마다 '**spk_0:**' 문단(word timestamp도 함께 켜진다)")
    ap.add_argument("--smart", action="store_true",
                    help="smart mode: 필러와 반복을 지우고 형식을 정리한다(기본은 verbatim)")
    ap.add_argument("--lang", metavar="CODES", help="BCP-47 언어 코드, 쉼표 구분. 없으면 자동 감지")
    ap.add_argument("--vocab", metavar="TERMS", help="인식 보정 용어, 쉼표 구분(최대 1,000개)")
    ap.add_argument("--vocab-file", metavar="PATH", help="한 줄에 한 용어. --vocab과 합친다")
    ap.add_argument("--plain", action="store_true", help="frontmatter 없이 본문만")
    args = ap.parse_args()

    # API가 함께 받지 않는 조합 — 조용히 한쪽을 끄지 않고 요청 전에 끝낸다.
    word_level = [o for o, on in (("--anchors", args.anchors is not None),
                                  ("--speakers", args.speakers)) if on]
    has_vocab = bool(args.vocab or args.vocab_file)
    if word_level and args.smart:
        ap.error(f"--smart는 {', '.join(word_level)}와 함께 쓸 수 없다(API 제약)")
    if word_level and has_vocab:
        ap.error(f"--vocab, --vocab-file은 {', '.join(word_level)}와 함께 쓸 수 없다(API 제약)")

    vocab = _split_terms(args.vocab or "", ",")
    if args.vocab_file:
        vf = pathlib.Path(args.vocab_file).expanduser()
        if not vf.is_file():
            die(f"vocab 파일이 없다: {vf}")
        vocab += _split_terms(vf.read_text(encoding="utf-8"), "\n")
    vocab = list(dict.fromkeys(vocab))
    if len(vocab) > VOCAB_MAX:
        die(f"vocab 용어가 {len(vocab):,}개다 — API 상한은 {VOCAB_MAX:,}개.")
    if len(vocab) > 100:
        log(f"경고: vocab 용어 {len(vocab)}개 — 공식 문서 권장치는 100개 안팎이다.")
    tcfg = transcription_config(args.anchors is not None, args.speakers, args.smart,
                                _split_terms(args.lang or "", ","), vocab)

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
        body = transcribe(src, args.anchors, tcfg, args.speakers)
    except RuntimeError as e:
        die(str(e))
    text = ("" if args.plain
            else frontmatter(src, args.anchors, duration, tcfg, args.speakers)) + body + "\n"
    if dest:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding="utf-8")
        log(f"저장: {dest} | {len(body.split()):,} 단어")
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    main()
