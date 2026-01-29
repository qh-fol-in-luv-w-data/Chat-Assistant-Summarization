import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from memory.schemas import SummaryOutput

def summarize(messages, model_name):
    llm = ChatGoogleGenerativeAI(model=model_name)

    prompt = ChatPromptTemplate.from_messages([
        ("system",
         """Summarize the conversation into structured JSON.
Schema:
{
  session_summary: {
    user_profile: {prefs: [], constraints: []},
    key_facts: [],
    decisions: [],
    open_questions: [],
    todos: []
  },
  message_range_summarized: {from: int, to: int}
}"""),
        ("human", "{messages}")
    ])

    chain = prompt | llm

    resp = chain.invoke({
        "messages": json.dumps(messages, indent=2)
    })

    return SummaryOutput.model_validate_json(resp.content)
