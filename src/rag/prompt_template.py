SYSTEM_PROMPT = """You are KnowSphere AI.
Answer ONLY using provided context.
Do not use outside knowledge.
If information is unavailable:
"I could not find this information in the provided documents."
"""

PROMPT_TEMPLATE = """SYSTEM:
{system_prompt}

CONVERSATION HISTORY:
{history}

CONTEXT:
{context}

QUESTION:
{question}

ANSWER:
"""

def build_prompt(question: str, context: str, history: str = "") -> str:
    """
    Compiles the system prompt, conversation history, dynamic context, and user question into the final LLM prompt.
    """
    return PROMPT_TEMPLATE.format(
        system_prompt=SYSTEM_PROMPT,
        history=history if history else "No prior conversation.",
        context=context,
        question=question
    )
