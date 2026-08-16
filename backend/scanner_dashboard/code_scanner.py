"""
소스코드 안에 하드코딩된 시크릿(API 키, 비밀번호, private key 등)이 있는지 찾는
스캐너예요. README 3대 축 중 "코드" 영역을 담당해요.
"""

import re
from pathlib import Path

PATTERNS = {
    "AWS Access Key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "API 키/비밀번호 변수": re.compile(r"(?i)(api[_-]?key|secret[_-]?key|password)\s*=\s*[\"'][^\"']{8,}[\"']"),
    "Private Key 블록": re.compile(r"-----BEGIN (RSA|EC|OPENSSH|PGP) PRIVATE KEY-----"),
}

EXCLUDED_DIRS = {".git", "node_modules", "venv", ".venv", "__pycache__", "migrations", "dist", "build"}
SCANNABLE_EXTENSIONS = {".py", ".js", ".jsx", ".ts", ".tsx", ".json", ".yml", ".yaml", ".tf"}


def scan_codebase(root_path: str) -> list[dict]:
    """
    root_path 아래 텍스트 파일들을 훑으면서 하드코딩된 시크릿 패턴을 찾아요.
    반환: [{"file": ..., "line": ..., "pattern_name": ..., "snippet": ...}, ...]
    """
    root = Path(root_path)
    findings = []

    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in EXCLUDED_DIRS for part in path.parts):
            continue
        if path.suffix not in SCANNABLE_EXTENSIONS:
            continue

        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        for line_no, line in enumerate(text.splitlines(), start=1):
            for pattern_name, pattern in PATTERNS.items():
                if pattern.search(line):
                    findings.append({
                        "file": str(path.relative_to(root)),
                        "line": line_no,
                        "pattern_name": pattern_name,
                        "snippet": line.strip()[:200],
                    })

    return findings
