"""
Career Chatbot — AI career advisor with user-profile awareness.

The chatbot knows the user's analysis result (score, matched skills, 
missing skills, target role) and provides personalized career advice.
"""
import os
from typing import Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

GROQ_MODEL = "openai/gpt-oss-20b"


def _build_system_prompt(user_profile: Dict[str, Any]) -> str:
    """Build the system prompt that injects the user's analysis context."""

    score = user_profile.get("score", 0)
    matched = user_profile.get("matched", [])
    partial = user_profile.get("partial", [])
    missing = user_profile.get("missing", [])
    role = user_profile.get("target_role", "the target role")

    return f"""You are CareerPilot, an expert AI career advisor for SkillBridge AI.

USER CONTEXT (their current analysis):
- Target Role: {role}
- Readiness Score: {score}%
- Matched Skills (they have): {', '.join(matched) if matched else 'none'}
- Partial Skills: {', '.join(partial) if partial else 'none'}
- Missing Skills (gaps): {', '.join(missing) if missing else 'none'}

YOUR RULES:
1. Always personalize answers using this user's actual skills and gaps.
2. When they ask "why", reference their SPECIFIC missing skills.
3. When they ask "what next", prioritize based on their gaps.
4. When they ask "should I apply", assess based on their score.
5. If they ask about something you don't know (like salary data or company-specific info), say so honestly.
6. Be concise: 3-5 sentences per answer. No long essays.
7. Be direct and encouraging, not overly formal.
8. Do NOT fabricate details about their profile.

Answer the user's question below."""


def career_chat(
    question: str,
    user_profile: Dict[str, Any],
    history: List[Dict[str, str]] = None
) -> str:
    """
    Answer a career question using the user's analysis as context.

    Args:
        question: The user's question
        user_profile: Dict with score, matched, partial, missing, target_role
        history: Optional list of {"role": "user"/"assistant", "content": "..."}

    Returns:
        The chatbot's response as a string.
    """
    from groq import Groq

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not set")

    client = Groq(api_key=api_key)

    # Build message list
    messages = [{"role": "system", "content": _build_system_prompt(user_profile)}]

    # Add conversation history (limit to last 6 messages to save tokens)
    if history:
        for msg in history[-6:]:
            messages.append({"role": msg["role"], "content": msg["content"]})

    # Add current question
    messages.append({"role": "user", "content": question})

    # Call Groq
    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            temperature=0.5,
            max_tokens=400,
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"⚠️ I'm having trouble responding right now ({str(e)[:80]}). Please try again."


# =================================================================
# STANDALONE TEST
# =================================================================
if __name__ == "__main__":
    test_profile = {
        "score": 80.0,
        "matched": ["Python", "FastAPI", "SQL", "PostgreSQL", "REST API"],
        "partial": ["TypeScript"],
        "missing": ["Docker", "AWS"],
        "target_role": "Backend Engineer",
    }

    test_questions = [
        "Why am I only 80% ready?",
        "What should I learn first?",
        "Can I apply now?",
    ]

    for q in test_questions:
        print(f"\n👤 USER: {q}")
        answer = career_chat(q, test_profile)
        print(f"🤖 BOT:  {answer}")
        print("-" * 60)