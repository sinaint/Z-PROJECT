"""
RAG(검색 후 생성)용 지식 베이스예요.
벡터DB 없이, query와 문서 사이 겹치는 단어 수로 관련 문서를 찾는 가장 단순한 검색이에요.
문서가 많아지면 embedding 기반 벡터 검색(예: chromadb)으로 교체하면 돼요.
"""

DOCUMENTS = [
    {
        "id": "s3-public-bucket",
        "category": "cloud",
        "title": "S3 버킷 퍼블릭 접근 차단",
        "text": (
            "S3 버킷이 퍼블릭으로 열려 있으면 누구나 인터넷에서 버킷 안의 파일을 읽거나 "
            "쓸 수 있어요. AWS 콘솔에서 'Block all public access' 설정을 켜고, "
            "버킷 정책(Bucket Policy)에서 Principal이 '*'로 되어 있는 규칙을 제거하세요. "
            "정적 웹사이트 등 퍼블릭 공개가 꼭 필요하면 CloudFront + OAC 조합을 쓰는 게 안전해요."
        ),
    },
    {
        "id": "iam-least-privilege",
        "category": "cloud",
        "title": "IAM 최소 권한 원칙",
        "text": (
            "IAM 사용자나 역할에 AdministratorAccess 같은 광범위한 권한을 주지 말고, "
            "실제로 필요한 서비스와 액션만 허용하는 최소 권한 정책을 적용하세요."
        ),
    },
    {
        "id": "iam-mfa-access-key",
        "category": "cloud",
        "title": "IAM MFA 및 Access Key 관리",
        "text": (
            "IAM 사용자에 MFA(다단계 인증)를 설정하지 않으면 비밀번호만 탈취돼도 계정이 "
            "뚫릴 수 있어요. 모든 사용자에 MFA를 활성화하고, Access Key는 90일 주기로 "
            "교체(rotate)하며 더 이상 쓰지 않는 키는 즉시 비활성화하거나 삭제하세요."
        ),
    },
    {
        "id": "sg-open-port",
        "category": "cloud",
        "title": "보안 그룹 인바운드 규칙 최소화",
        "text": (
            "보안 그룹에서 0.0.0.0/0(모든 IP)에 SSH(22), RDP(3389), DB 포트(3306, 5432 등)를 "
            "열어두면 전 세계 누구나 접속을 시도할 수 있어요. 접속이 필요한 특정 IP 대역만 "
            "허용하거나, VPN이나 Bastion Host를 통해서만 접근하도록 제한하세요."
        ),
    },
    {
        "id": "hardcoded-secret",
        "category": "code",
        "title": "코드에 하드코딩된 시크릿",
        "text": (
            "API 키, 비밀번호, AWS Access Key 같은 민감 정보를 소스코드에 직접 적으면 "
            "git 이력에 영구히 남고 저장소가 공개되는 순간 바로 탈취돼요. "
            "환경변수(.env)나 AWS Secrets Manager로 옮기고, 이미 커밋된 키는 반드시 "
            "폐기(rotate)하고 새 키로 교체하세요."
        ),
    },
    {
        "id": "phishing-url",
        "category": "phishing",
        "title": "피싱 의심 URL/이메일",
        "text": (
            "발신자 도메인이 정식 도메인과 미묘하게 다르거나(오타 도메인), 긴급성을 "
            "강조하며 링크 클릭이나 로그인 정보 입력을 유도하는 이메일은 피싱일 가능성이 "
            "높아요. 링크를 직접 클릭하지 말고 공식 사이트 주소로 직접 접속해서 확인하세요."
        ),
    },
]


def retrieve_relevant_docs(query: str, category: str | None = None, top_k: int = 2):
    """query와 겹치는 단어가 많은 문서를 top_k개 찾아 반환해요."""
    query_words = set(query.lower().split())
    candidates = DOCUMENTS if category is None else [d for d in DOCUMENTS if d["category"] == category]

    scored = []
    for doc in candidates:
        doc_words = set((doc["title"] + " " + doc["text"]).lower().split())
        overlap = len(query_words & doc_words)
        if overlap > 0:
            scored.append((overlap, doc))

    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [doc for _, doc in scored[:top_k]] if scored else candidates[:top_k]
