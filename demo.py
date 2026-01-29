import json
from config import *
from memory.session_store import SessionStore
from memory.context_manager import ContextManager
from query.pipeline import run_query_pipeline
from langchain_google_genai import ChatGoogleGenerativeAI


def load_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def demo_session_memory():
    print("\n==============================")
    print("FLOW 1 — SESSION MEMORY DEMO")
    print("==============================")

    store = SessionStore(SESSION_FILE)
    ctx_mgr = ContextManager(store, MAX_CONTEXT_TOKENS, MODEL_NAME)

    messages = load_jsonl("data/test_long.jsonl")

    for i, msg in enumerate(messages, 1):
        store.add_message(msg["role"], msg["content"])
        tokens = ctx_mgr.context_size()

        print(f"[{i}] Context tokens: {tokens}")

        summary = ctx_mgr.check_and_summarize()
        if summary:
            print("\n Context limit exceeded → summarizing")
            print(" Generated summary:")
            print(json.dumps(summary, indent=2, ensure_ascii=False))
            break


def demo_ambiguous_query():
    print("\n==============================")
    print(" FLOW 2 — AMBIGUOUS QUERY DEMO")
    print("==============================")

    llm = ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        temperature=0.3
    )

    test_queries = load_jsonl("data/test_ambiguous.jsonl")
    query = test_queries[0]["query"]

    store = SessionStore(SESSION_FILE)
    data = store.load()

    recent = data["messages"][-RECENT_MESSAGES_N:]
    summary = data.get("summary")

    result = run_query_pipeline(
        llm=llm,
        query=query,
        recent=recent,
        summary=summary
    )

    analysis = result["analysis"]

    print("User query:", query)
    print("\n Analysis:")
    print(json.dumps(analysis, indent=2, ensure_ascii=False))

    print("\n Assistant response:")

    # ===  FLOW 2 DECISION LOGIC (QUAN TRỌNG) ===
    if analysis.get("is_ambiguous", False):
        questions = analysis.get("clarifying_questions", [])
        if questions:
            print(questions[0])
        else:
            print("Mình chưa chắc đã hiểu đúng ý bạn, bạn có thể nói rõ hơn không?")
    else:
        print(result["final_answer"])

if __name__ == "__main__":
    demo_session_memory()
    demo_ambiguous_query()
