"""
피싱 의심 URL/이메일 탐지 로직
=========================
README 3대 축 중 "사람(피싱)" 영역을 담당해요.
S3나 코드처럼 "전체를 훑는" 스캔이 아니라, 사용자가 의심스러운 URL이나
이메일 본문을 직접 입력하면 그 안에 피싱 징후가 있는지 규칙 기반으로 점검해요.
"""

import re
from urllib.parse import urlparse

# URL 단축 서비스예요. 실제 목적지를 가려서 피싱에 자주 악용돼요.
SHORTENER_DOMAINS = {"bit.ly", "tinyurl.com", "t.co", "goo.gl", "is.gd", "ow.ly", "buff.ly"}

# 저렴하거나 무료로 많이 발급돼서 피싱 사이트에 자주 쓰이는 TLD예요.
SUSPICIOUS_TLDS = {"zip", "mov", "top", "xyz", "click", "work", "support", "gq", "cf", "tk", "ml"}

# 이메일/문자 본문에서 "긴급성"을 강조해 판단력을 흐리는 대표적인 문구들이에요.
URGENCY_KEYWORDS = [
    "즉시", "긴급", "계정이 정지", "24시간 이내", "지금 확인하지 않으면",
    "비밀번호를 확인", "결제 정보를 업데이트", "당첨되셨습니다",
]

# 텍스트 안에서 URL을 찾아내기 위한 느슨한 패턴이에요.
URL_PATTERN = re.compile(r"https?://[^\s]+|(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(?:/[^\s]*)?")


def analyze_url(url: str) -> list[str]:
    """
    URL 하나를 뜯어봐서 의심스러운 특징이 있으면 이유(reason) 리스트로 반환해요.
    """
    reasons = []
    raw = url if "://" in url else f"http://{url}"
    parsed = urlparse(raw)
    host = (parsed.hostname or "").lower()

    # "@" 앞부분은 브라우저가 로그인 정보로 취급하고, 진짜 목적지는 "@" 뒤예요.
    # naver.com@evil.com 처럼 진짜 도메인인 척 눈속임하는 전형적인 수법이에요.
    authority = raw.split("://", 1)[-1].split("/", 1)[0]
    if "@" in authority:
        reasons.append("URL에 '@' 기호가 포함되어 있음 (실제 목적지를 속이는 전형적인 수법)")

    # 도메인 이름 없이 IP 주소를 직접 노출하는 경우예요.
    is_ip_host = bool(re.match(r"^\d{1,3}(\.\d{1,3}){3}$", host))
    if is_ip_host:
        reasons.append("도메인 대신 IP 주소를 직접 사용함")

    # 퓨니코드(punycode)는 한글/키릴 문자 등으로 알파벳을 흉내내는 도메인(homograph)에 쓰여요.
    if host.startswith("xn--") or ".xn--" in host:
        reasons.append("퓨니코드(punycode) 도메인 - 눈속임 문자(homograph) 가능성")

    if any(host == d or host.endswith("." + d) for d in SHORTENER_DOMAINS):
        reasons.append(f"URL 단축 서비스({host}) 사용 - 실제 목적지를 숨길 수 있음")

    tld = host.rsplit(".", 1)[-1] if "." in host else ""
    if tld in SUSPICIOUS_TLDS:
        reasons.append(f"피싱에 자주 악용되는 TLD(.{tld}) 사용")

    # 서브도메인이 과도하게 많으면(예: login.account.verify.naver.com.evil.top)
    # 진짜 도메인처럼 보이게 하려는 시도일 수 있어요. (IP 주소는 해당 없음)
    if not is_ip_host and host.count(".") >= 3:
        reasons.append(f"서브도메인이 비정상적으로 많음 ({host})")

    return reasons


def analyze_text(text: str) -> list[str]:
    """
    이메일/문자 본문 전체를 점검해요.
    긴급성 강조 문구 + 본문 안에 포함된 URL들을 같이 확인해요.
    """
    reasons = []

    for keyword in URGENCY_KEYWORDS:
        if keyword in text:
            reasons.append(f"긴급성을 강조하는 문구 발견: '{keyword}'")
            break  # 하나만 찾아도 충분히 의심스러우니 여러 개 나열하진 않아요

    for url in URL_PATTERN.findall(text):
        reasons.extend(analyze_url(url))

    return reasons


def scan_input(raw_input: str) -> dict:
    """
    사용자가 입력한 문자열(URL 하나 또는 이메일 본문)을 점검해요.

    반환 형태 예시:
    {"is_risky": True, "reasons": ["URL 단축 서비스(bit.ly) 사용 - ..."]}
    """
    raw_input = (raw_input or "").strip()
    if not raw_input:
        return {"is_risky": False, "reasons": []}

    # 공백이 없고 "."이 있으면 URL 하나로, 그렇지 않으면 이메일 본문(긴 텍스트)으로 봐요.
    looks_like_single_url = " " not in raw_input and "." in raw_input
    reasons = analyze_url(raw_input) if looks_like_single_url else analyze_text(raw_input)

    return {"is_risky": bool(reasons), "reasons": reasons}
