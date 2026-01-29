import json
import re
from langchain_core.prompts import ChatPromptTemplate


# =========================
# UTILS
# =========================
def extract_json(text: str):
    """
    Robust JSON extractor for LLM outputs.
    Extracts the first {...} block and parses it.
    """
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        raise ValueError("No JSON found in LLM output")
    return json.loads(match.group())


def heuristic_vietnamese_rewrite(text: str) -> str:
    """
    Very lightweight heuristic rewrite for common Vietnamese typos.
    Used ONLY as a fallback when LLM output is broken.
    """
    rules = {
        "dawng": "đang",
        "awn": "ăn",
        "com": "cơm",
        "khog": "không",
        "ko": "không",
        "dc": "được",
    }
    words = text.split()
    return " ".join(rules.get(w.lower(), w) for w in words)


# =========================
# MAIN PIPELINE
# =========================
def run_query_pipeline(llm, query, recent, summary):
    """
    Pipeline logic (SCHEMA-ALIGNED):

    1. Analyze ambiguity using a strict JSON schema
    2. If ambiguous → ONLY ask clarifying questions
    3. If clear → respond normally

    IMPORTANT:
    - NEVER answer when clarification is required
    - JSON schema is fixed and consistent
    """

    # =========================
    # STAGE 0: AMBIGUITY ANALYSIS
    # =========================
    AMBIGUOUS_PROMPT = ChatPromptTemplate.from_template("""
You are analyzing a user query in a conversational AI system.

Conversation summary:
{summary}

Recent messages:
{recent}

User query:
{query}

Task:
Determine whether the user query is ambiguous.

A query is considered ambiguous if:
- It contains heavy typos or unclear wording
- Multiple interpretations are possible
- The intent cannot be confidently determined from the query alone

Return STRICT JSON in the following format:
{{
  "original_query": string,
  "is_ambiguous": true | false,
  "rewritten_query": string | null,
  "needed_context_from_memory": array of strings,
  "clarifying_questions": array of strings,
  "final_augmented_context": string
}}

Field guidelines:

- original_query:
  - Must be EXACTLY the user query, unchanged

- is_ambiguous:
  - true if intent is unclear or uncertain
  - false only if the intent is fully clear

- rewritten_query:
  - If is_ambiguous = true, provide your best normalized or corrected version
  - If is_ambiguous = false, set this to null

- needed_context_from_memory:
  - List memory signals that could help clarify the user's intent
  - Include items EVEN IF they are optional but potentially useful
  - Examples:
    - "recent_topic"
    - "conversation_state"
    - "open_questions"
    - "user_preferences"
  - If the query does NOT clearly relate to the immediately previous topic,
    you MUST include at least one memory signal

clarifying_questions:
- Questions must clarify the MEANING or INTENT of the original query
- Questions should focus on:
  - confirming the rewritten interpretation
  - checking if the user made a typo
  - asking whether the query relates to the previous topic
- DO NOT ask generic follow-up or conversational questions
- Each question should help reduce uncertainty about what the user meant


- final_augmented_context:
  - Briefly explain how the rewritten query and memory signals
    would be combined to resolve ambiguity

Rules:
- DO NOT answer the user.
- DO NOT include explanations outside the JSON.
- Emotional or informal language can still be non-ambiguous.
- If heavy typos exist, the query MUST be considered ambiguous.
- The JSON must be valid and directly parseable.

""")

    resp = (AMBIGUOUS_PROMPT | llm).invoke({
        "query": query,
        "recent": recent,
        "summary": summary or "No prior summary."
    })

    # =========================
    # PARSE + SAFE FALLBACK
    # =========================
    try:
        analysis = extract_json(resp.content)
    except Exception:
        rewrite = heuristic_vietnamese_rewrite(query)
        analysis = {
            "original_query": query,
            "is_ambiguous": True,
            "rewritten_query": rewrite,
            "needed_context_from_memory": [],
            "clarifying_questions": [
                f"Mình đoán bạn muốn nói: \"{rewrite}\". Mình hiểu đúng không?"
            ],
            "final_augmented_context": ""
        }

    # =========================
    # FLOW 2: AMBIGUOUS → ASK ONLY
    # =========================
    if analysis.get("is_ambiguous", True):
        questions = analysis.get("clarifying_questions")
        if not questions:
            questions = [
                "Mình chưa chắc đã hiểu đúng ý bạn, bạn có thể nói rõ hơn không?"
            ]

        return {
            "analysis": analysis,
            "final_answer": "\n".join(questions)
        }

    # =========================
    # FLOW 1: CLEAR → NORMAL RESPONSE
    # =========================
    RESPONSE_PROMPT = ChatPromptTemplate.from_template("""
You are a helpful chat assistant.

Conversation summary:
{summary}

Recent messages:
{recent}

User input:
{query}

Respond naturally and appropriately.
""")

    resp = (RESPONSE_PROMPT | llm).invoke({
        "query": query,
        "recent": recent,
        "summary": summary or "No prior summary."
    })

    return {
        "analysis": analysis,
        "final_answer": resp.content
    }
