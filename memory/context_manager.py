import json
import re
import tiktoken
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate


class ContextManager:
    def __init__(self, store, max_tokens, model_name):
        self.store = store
        self.max_tokens = max_tokens
        self.model_name = model_name
        self.encoder = tiktoken.get_encoding("cl100k_base")

    # =========================
    # UTILS
    # =========================
    def _count_tokens(self, text: str) -> int:
        return len(self.encoder.encode(text))

    def _extract_json(self, text: str):
        match = re.search(r"\{[\s\S]*\}", text)
        if not match:
            raise ValueError("No JSON found")
        return json.loads(match.group())

    def _empty_summary(self, start, end):
        return {
            "session_summary": {
                "user_profile": {
                    "prefs": [],
                    "constraints": []
                },
                "key_facts": [],
                "decisions": [],
                "open_questions": [],
                "todos": []
            },
            "message_range_summarized": {
                "from": start,
                "to": end
            }
        }

    # =========================
    # CONTEXT SIZE
    # =========================
    def context_size(self) -> int:
        data = self.store.load()
        total = 0

        if data.get("summary"):
            total += self._count_tokens(json.dumps(data["summary"]))

        for m in data.get("messages", []):
            total += self._count_tokens(m["content"])

        return total

    # =========================
    # MAIN LOGIC
    # =========================
    def check_and_summarize(self):
        tokens = self.context_size()

        if tokens < self.max_tokens:
            return None

        data = self.store.load()
        messages = data.get("messages", [])

        if not messages:
            return None

        # === PREP CONVERSATION ===
        convo = "\n".join(
            f"{m['role']}: {m['content']}" for m in messages
        )

        start_idx = 0
        end_idx = len(messages) - 1

        llm = ChatGoogleGenerativeAI(
            model=self.model_name,
            temperature=0
        )

        prompt = ChatPromptTemplate.from_template("""
You are summarizing a conversation for long-term memory.

Return STRICT JSON in the following format:
{{
  "session_summary": {{
    "user_profile": {{
      "prefs": [],
      "constraints": []
    }},
    "key_facts": [],
    "decisions": [],
    "open_questions": [],
    "todos": []
  }}
}}

Guidelines:
- Only extract information that is explicitly stated or strongly implied
- Do NOT invent facts
- Use empty arrays if nothing is found
- Output JSON only, no explanation

Conversation:
{conversation}

""")

        raw = (prompt | llm).invoke(
            {"conversation": convo}
        ).content

        # === PARSE / FALLBACK ===
        try:
            parsed = self._extract_json(raw)
            summary = {
                **parsed,
                "message_range_summarized": {
                    "from": start_idx,
                    "to": end_idx
                }
            }
        except Exception:
            summary = self._empty_summary(start_idx, end_idx)

        # === SAVE ===
        self.store.save({
            "messages": [],
            "summary": summary
        })

        return summary
