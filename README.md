# 🛡️ Z-PROJECT

> 클라우드 인프라 · 코드 · 사람(피싱), 세 가지 보안 구멍을 AI가 찾아주고 쉽게 설명해주는 보안 코파일럿

## 👥 팀 & 역할

| 이름 | 역할 | 담당 영역 |
|---|---|---|
| ZERO | 클라우드 보안 / 인프라 | AWS(S3, IAM, VPC, Security Group), Terraform, boto3 |
| 형 | 백엔드 / AI 연동 | Django or Spring Boot, GPT-4o/Claude API, RAG |

## 📁 폴더 구조

```
Z-PROJECT/
├── backend/          # API 서버 (Django/Spring Boot) - 형 담당
├── infra/
│   └── terraform/    # AWS 인프라 코드 (IaC) - ZERO 담당
├── frontend/         # 대시보드 (React)
├── docs/             # 회의록, 아키텍처 다이어그램 등 문서
│   └── architecture.mermaid
├── .gitignore
└── README.md
```

## 🚀 로컬 개발 환경 세팅 (추후 작성 예정)

```bash
# 1. 레포 클론
git clone https://github.com/sinaint/Z-PROJECT.git
cd Z-PROJECT

# 2. 각 파트별 세팅은 backend/README.md, infra/README.md 참고
```

## 🌱 브랜치 전략

- `main` : 항상 정상 동작하는 상태만 유지 (직접 push 금지, PR로만 병합)
- `feature/기능이름` : 새 기능 작업할 때마다 새 브랜치 생성
  - 예: `feature/aws-scanner`, `feature/rag-report`
- 작업 끝나면 GitHub에서 Pull Request 생성 → 서로 리뷰 후 병합

## ⚠️ 보안 체크리스트 (작업 전 꼭 확인!)

- [ ] AWS Access Key/Secret Key는 절대 코드에 하드코딩 X → `.env` 또는 AWS Secrets Manager 사용
- [ ] `.env` 파일은 `.gitignore`에 포함되어 있는지 확인
- [ ] Terraform 상태 파일(`*.tfstate`)은 절대 커밋 X
- [ ] LLM API 키(OpenAI/Gemini/Claude)도 동일하게 환경변수로 관리

## 📝 진행 상황

- [x] 프로젝트 아이디어 논의
- [x] 초기 아키텍처 설계
- [ ] MVP 기능 범위 확정
- [ ] 개발 시작
