"""
스캔 결과를 Claude API에 보내서 "왜 위험한지 + 어떻게 고치는지"를 설명받는 모듈이에요.
RAG: knowledge_base에서 관련 문서를 먼저 찾고(retrieve), 그 내용을 프롬프트에 같이
넣어서(augmented) 더 근거 있는 답을 생성(generate)하게 해요.
"""

import anthropic
from django.conf import settings

from .knowledge_base import retrieve_relevant_docs

# 실제 서비스에 배포할 모델은 https://docs.anthropic.com/en/docs/about-claude/models
# 에서 최신 모델 ID를 확인하고 필요하면 바꿔주세요.
MODEL_NAME = "claude-sonnet-4-5-20250929"

_client = None


def _get_client():
    global _client
    if _client is None and settings.ANTHROPIC_API_KEY:
        _client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    return _client


def explain_finding(category: str, target: str, is_risky: bool, detail: str = "") -> str:
    """
    스캔 결과 하나를 자연어로 설명해줘요.
    ANTHROPIC_API_KEY가 없으면 에러 대신 안내 문구를 반환해요.
    """
    if not is_risky:
        return "특별한 위험이 발견되지 않았어요."

    client = _get_client()
    if client is None:
        return "(ANTHROPIC_API_KEY가 설정되지 않아 AI 설명을 생성할 수 없어요. backend/.env를 확인하세요.)"

    docs = retrieve_relevant_docs(f"{category} {target} {detail}", category=category, top_k=2)
    reference_text = "\n".join(f"- {d['title']}: {d['text']}" for d in docs)

    prompt = f"""당신은 보안 코파일럿이에요. 아래 스캔 결과를 보안 지식이 적은 사람도 이해할 수 있게
한국어로 짧고 명확하게 설명해주세요.

[스캔 결과]
- 영역: {category}
- 대상: {target}
- 상세: {detail or '없음'}

[참고 자료]
{reference_text}

3~4문장 이내로, (1) 왜 위험한지 (2) 어떻게 고치는지 순서로 답해주세요."""

    try:
        response = client.messages.create(
            model=MODEL_NAME,
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text.strip()
    except anthropic.APIError as e:
        return f"(AI 설명 생성 중 오류가 발생했어요: {e})"
