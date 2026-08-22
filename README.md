# 🛡️ Z-PROJECT

> 클라우드 인프라 · 코드 · 사람(피싱), 세 가지 보안 구멍을 AI가 찾아주고 쉽게 설명해주는 보안 코파일럿

## 📌 프로젝트 소개

보안 지식이 많지 않은 사람도 "지금 우리 시스템에 어떤 위험이 있는지"를 한눈에 볼 수 있게 만든 대시보드예요.
세 가지 영역을 스캔하고, 위험이 발견되면 **RAG(문서 검색) + Claude API**로 "왜 위험한지 / 어떻게 고치는지"를 자연어로 설명해줘요.

| 영역 | 점검 항목 |
|---|---|
| ☁️ 클라우드 | S3 퍼블릭 버킷, IAM(과도한 권한·MFA 미설정·오래된 Access Key), 보안 그룹(0.0.0.0/0 오픈 포트) |
| 🧑‍💻 코드 | 하드코딩된 API 키/비밀번호/Private Key |
| 🎣 사람(피싱) | 의심스러운 URL·이메일 (오타 도메인, 단축 URL, IP 직접 노출, 긴급성 강조 문구 등) |

## 👥 팀 & 역할

| 이름 | 역할 |
|---|---|
| ZERO | 클라우드 보안/인프라(AWS, Terraform) + 백엔드/AI 연동(Django, Claude API, RAG) + 프론트엔드(React) 전체 담당 |

> 원래 백엔드/AI는 팀원이 같이 맡았지만 팀원이 취업하면서 현재는 ZERO 혼자 이어가고 있어요.

## 🏗️ 아키텍처

전체 데이터 흐름은 [`docs/architecture.mermaid`](docs/architecture.mermaid)에 정리되어 있어요.

```
브라우저(React or Django 템플릿)
    │  로그인 세션 + CSRF
    ▼
Django REST API (api_views.py)
    │
    ├─ scanner.py         → boto3 → AWS(S3 · IAM · EC2 보안그룹)
    ├─ code_scanner.py    → 파일시스템 정규식 스캔
    └─ phishing_scanner.py → URL/이메일 규칙 기반 점검
    │
    ▼
ai_explainer.py ── (RAG) knowledge_base.py에서 관련 문서 검색 ── Claude API 호출
    │
    ▼
ScanResult 모델 → SQLite (db.sqlite3, 로컬 전용·git 추적 제외)
```

## ✨ 주요 기능

- **클라우드/코드/피싱 3대 축 스캐너** — 위 표 참고
- **AI 설명(RAG)** — 스캔 결과를 `knowledge_base.py`의 참고 문서와 함께 Claude API에 보내서, 보안 지식이 없어도 이해할 수 있는 설명 생성
- **로그인 인증** — 대시보드/API 전부 로그인 필요 (`django.contrib.auth`)
- **Django 템플릿 대시보드 + React 대시보드** — 같은 API를 기반으로 두 가지 프론트엔드 제공
- **Terraform IaC** — 스캐너 테스트용 AWS 리소스(S3/보안그룹)를 코드로 재현 가능하게 관리 (`infra/terraform/`)

## 📁 폴더 구조

```
Z-PROJECT/
├── backend/                    # Django API 서버
│   ├── config/                 # 프로젝트 설정 (settings, urls)
│   ├── scanner_dashboard/      # 스캐너 앱 (모델, 뷰, API, 스캐너 로직)
│   │   ├── scanner.py          # S3 / IAM / 보안그룹 스캐너
│   │   ├── code_scanner.py     # 하드코딩 시크릿 스캐너
│   │   ├── phishing_scanner.py # 피싱 URL/이메일 스캐너
│   │   ├── ai_explainer.py     # Claude API 호출 (RAG)
│   │   └── knowledge_base.py   # RAG용 참고 문서
│   ├── templates/               # Django 템플릿 대시보드
│   └── .env.example             # 필요한 환경변수 목록
├── frontend/                   # React 대시보드 (Vite)
├── infra/
│   └── terraform/               # AWS 인프라 코드 (IaC) - 스캐너 테스트용
├── docs/
│   └── architecture.mermaid     # 아키텍처 다이어그램
├── .gitignore
└── README.md
```

## 🚀 로컬 개발 환경 세팅

### 1. 레포 클론

```bash
git clone https://github.com/sinaint/Z-PROJECT.git
cd Z-PROJECT
```

### 2. 백엔드 (Django)

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate / macOS·Linux: source .venv/bin/activate
pip install -r requirements.txt

# .env 파일 만들기
copy .env.example .env   # Windows / macOS·Linux는 cp
# .env 파일 열어서 SECRET_KEY, ANTHROPIC_API_KEY, AWS 자격증명 채우기
# SECRET_KEY는 아래 명령으로 새로 발급받으세요:
#   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

python manage.py migrate
python manage.py createsuperuser   # 로그인용 계정 생성
python manage.py runserver
```

`http://127.0.0.1:8000` 접속 → 로그인 후 Django 템플릿 대시보드 사용 가능.

### 3. 프론트엔드 (React, 선택)

```bash
cd frontend
npm install
npm run dev
```

`http://localhost:5173` 접속. (Vite 프록시 설정 덕분에 Django 로그인 세션을 그대로 공유해요. 위 Django 서버가 8000번 포트에 떠 있어야 해요.)

### 4. AWS 스캐너 실행 전 준비

- `aws configure`로 자격증명 등록 (스캐너용 계정은 읽기 전용 최소 권한 권장: `s3:ListAllMyBuckets`, `s3:GetBucketPolicyStatus`, `iam:ListUsers`, `iam:ListAttachedUserPolicies`, `iam:ListMFADevices`, `iam:ListAccessKeys`, `iam:GetLoginProfile`, `ec2:DescribeSecurityGroups`)

## 🌱 브랜치 전략

- `main` : 항상 정상 동작하는 상태만 유지 (직접 push 금지, PR로만 병합)
- `feature/기능이름` : 새 기능 작업할 때마다 새 브랜치 생성
- 작업 끝나면 GitHub에서 Pull Request 생성 → 리뷰 후 병합

## ⚠️ 보안 체크리스트

- [x] AWS Access Key/Secret Key는 절대 코드에 하드코딩 X → `.env` 사용
- [x] `.env` 파일은 `.gitignore`에 포함
- [x] Terraform 상태 파일(`*.tfstate`)은 절대 커밋 X
- [x] LLM API 키(Claude)도 동일하게 환경변수로 관리
- [x] Django `SECRET_KEY`도 환경변수로 분리
- [x] `db.sqlite3`(로그인 비밀번호 해시 등 민감정보 포함)는 git 추적 제외
- [x] 대시보드/API에 로그인 인증 적용

## 🐛 트러블슈팅 기록

개발하면서 겪은 문제와 해결 과정이에요. (실제로 찾아서 고친 것들)

- **`TemplateDoesNotExist`** — `TEMPLATES["DIRS"]`가 비어있어서 프로젝트 루트 `templates/`를 못 찾던 문제. `DIRS: [BASE_DIR / "templates"]` 추가로 해결.
- **`SECRET_KEY` 하드코딩 노출** — 코드 스캐너가 자기 자신의 `settings.py`에서 실제로 하드코딩된 `SECRET_KEY`를 탐지. `git blame`으로 최초 커밋 추적 후, 새 키 발급 + `.env`로 이동.
- **IAM MFA 오탐** — 콘솔 로그인이 꺼진 서비스 계정(스캐너 전용 IAM 사용자)까지 "MFA 미설정"으로 잡던 문제. `iam:GetLoginProfile`로 콘솔 로그인 가능 여부를 먼저 확인하도록 로직 개선.
- **React ↔ Django 인증 연동** — 별도 포트(5173)에서 Django 세션 쿠키를 쓰려면 보통 CORS 설정이 필요한데, Vite의 `server.proxy`로 `/api`, `/accounts`를 Django(8000)로 그대로 전달해서 브라우저 입장에선 동일 origin으로 보이게 만들어 CORS 없이 해결.

## 📝 진행 상황

- [x] 프로젝트 아이디어 논의 / 초기 아키텍처 설계
- [x] 클라우드 스캐너 (S3 / IAM / 보안 그룹)
- [x] 코드 스캐너 (하드코딩 시크릿)
- [x] 피싱 스캐너 (URL / 이메일 규칙 기반)
- [x] AI 설명(RAG) 연동
- [x] 로그인 인증
- [x] React 프론트엔드
- [x] Terraform IaC (코드 작성, 실제 적용은 필요시 진행)
- [ ] 배포 (현재는 로컬 개발 환경만 지원)
