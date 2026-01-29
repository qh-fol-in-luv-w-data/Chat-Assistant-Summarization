from config import *
from memory.session_store import SessionStore
from memory.context_manager import ContextManager
from query.pipeline import run_query_pipeline
import json

# 🔹 khởi tạo LLM (ví dụ Gemini qua LangChain)
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model=MODEL_NAME,
    temperature=0.3
)

store = SessionStore(SESSION_FILE)
ctx_mgr = ContextManager(store, MAX_CONTEXT_TOKENS, MODEL_NAME)

print("💬 Chat Assistant (type 'exit' to quit)")

while True:
    user_input = input("\nUser: ")
    if user_input.lower() == "exit":
        break

    store.add_message("user", user_input)

    # === FLOW 1: SESSION MEMORY TRIGGER ===
    summary = ctx_mgr.check_and_summarize()
    if summary:
        print("✅ Session summary generated:")
        print(summary)

    # === FLOW 2: QUERY UNDERSTANDING ===
    data = store.load()
    recent = data["messages"][-RECENT_MESSAGES_N:]
    session_summary = data.get("summary")

    result = run_query_pipeline(
        llm=llm,
        query=user_input,
        recent=recent,
        summary=session_summary
    )

    print("\n🧠 Query Understanding Output:")
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # In câu trả lời cho user
    print("\nAssistant:", result["final_answer"])

    store.add_message("assistant", result["final_answer"])
