from pydantic import BaseModel
from typing import List, Dict, Optional

class SessionSummary(BaseModel):
    user_profile: Dict[str, list]
    key_facts: List[str]
    decisions: List[str]
    open_questions: List[str]
    todos: List[str]

class SummaryOutput(BaseModel):
    session_summary: SessionSummary
    message_range_summarized: Dict[str, int]


class QueryUnderstandingOutput(BaseModel):
    original_query: str
    is_ambiguous: bool
    rewritten_query: Optional[str]
    needed_context_from_memory: List[str]
    clarifying_questions: List[str]
    final_augmented_context: str
