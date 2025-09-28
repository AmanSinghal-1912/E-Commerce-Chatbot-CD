from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os
load_dotenv()

# Initialize LLM
llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.1-8b-instant",
    temperature=0.3  # slightly higher for more natural responses
)

def reflection_agent(db_output: str, policy_output: str, previous_context: str = "", max_iterations: int = 3):
    """
    Combines DB + Policy outputs into a user-friendly final response.
    Motivates LLM to generate customer-friendly one-liners when asked 'why should I buy this?'
    Maintains context from previous interactions.
    """
    # Greeting shortcut
    is_greeting = (not db_output and not policy_output and 
                  (not previous_context or len(previous_context) < 50))
    
    if is_greeting:
        return "Hello! I can help with product information and company policies. What would you like to know?"
        
    prompt_template = ChatPromptTemplate.from_template(
        """
        You are a helpful product advisor and policy assistant. 
        Your task is to combine the database and policy information into a natural, customer-friendly response.

        Previous context: {previous_context}
        Database information: {db_output}
        Policy information: {policy_output}

        Guidelines:
        - Be direct and professional, avoid phrases like "Based on the previous context".
        - If the user asks "why should I buy this?" or "explain with info you have", 
          create a short **one-liner sales pitch** from the database fields.
            * Highlight strongest selling points: price, warranty, rating, stock, category.
            * Keep under 20 words, persuasive, and based ONLY on provided info.
        - If the query is about policies, explain clearly and concisely in 2–3 sentences.
        - If both db and policy info are empty but there’s previous context, continue naturally.
        - Keep answers short and helpful (max 3–4 sentences unless user explicitly asks for more).
        """
    )
    
    response = ""
    for i in range(max_iterations):
        formatted_prompt = prompt_template.format_messages(
            db_output=db_output,
            policy_output=policy_output,
            previous_context=previous_context
        )
        candidate = llm.invoke(formatted_prompt).content

        reflection_check = llm.invoke(
            f"Does the following response meet the guidelines (concise, relevant, persuasive if needed, no extra greetings)? "
            f"Answer YES or NO.\n\nResponse:\n{candidate}"
        )

        response = candidate
        if "YES" in reflection_check.content.upper():
            break

    return response

__all__ = ["reflection_agent"]
