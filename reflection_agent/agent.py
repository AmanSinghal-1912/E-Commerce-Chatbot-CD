# realtime_db_agent/reflection_agent.py
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize LLM
llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.3-70b-versatile",
    temperature=0.4  # Balanced for natural conversation
)

def _is_response_high_quality(response: str, user_query: str) -> bool:
    """Fast, rule-based quality check to avoid robotic or low-effort responses."""
    response = response.strip()
    
    # Too short or empty?
    if len(response) < 15:
        return False
        
    # Avoid robotic/templated phrasing
    robotic_phrases = [
        "based on", "according to", "here is", "i found", 
        "the database shows", "policy states", "as per",
        "i have retrieved", "the information shows"
    ]
    if any(phrase in response.lower() for phrase in robotic_phrases):
        return False
        
    # Avoid generic "no info" responses that are too brief
    if ("no specific" in response.lower() or "don't have" in response.lower()) and len(response.split()) < 20:
        return False
        
    # Basic relevance check: response should attempt to address the query
    if not response.endswith(('.', '!', '?')):
        return False
        
    return True

def _generate_fallback_response(user_query: str) -> str:
    """Generate a safe fallback response when primary generation fails."""
    fallback_prompt = f"""
    The user asked: "{user_query}"
    
    Provide a brief, helpful response. If you can't answer specifically, politely explain what you can help with instead.
    Keep it conversational and friendly. Do not mention databases or internal systems.
    """
    try:
        return llm.invoke(fallback_prompt).content.strip()
    except:
        return "I'm sorry, I'm having trouble processing that right now. Could you rephrase your question or ask something else?"

def reflection_agent(
    db_output: str = "", 
    policy_output: str = "", 
    previous_context: str = "", 
    user_query: str = "", 
    max_iterations: int = 1  # Reduced from 2 - one high-quality pass is sufficient
):
    """
    Synthesizes responses from DB and Policy agents into natural, conversational responses.
    Handles context awareness and general conversation naturally.
    """
    
    # Input sanitization
    db_output = str(db_output) if db_output else ""
    policy_output = str(policy_output) if policy_output else ""
    previous_context = str(previous_context) if previous_context else ""
    user_query = str(user_query).strip() if user_query else ""
    
    if not user_query:
        return "I'm here to help! Could you please ask your question?"
    
    # Main conversation prompt with strong anti-hallucination guardrails
    conversation_prompt = ChatPromptTemplate.from_template(
        """
        You are a friendly, helpful assistant having a natural conversation with a customer. 

        Current situation:
        - User asked: "{user_query}"
        - Previous conversation context: {previous_context}
        - Database information available: {db_output}
        - Policy information available: {policy_output}

        Your role:
        1. Respond naturally like a human customer service representative
        2. If you have database info, integrate it smoothly into your response
        3. If you have policy info, explain it in a conversational way
        4. If you have both, blend them naturally - don't treat them as separate sections
        5. If you have neither but the user is asking something general, respond helpfully
        6. Maintain conversation flow - reference previous context when relevant
        7. Keep responses conversational length (2-4 sentences typically)
        8. Be warm and professional, not robotic

        IMPORTANT SAFETY RULES:
        - NEVER invent product details, prices, policies, or availability not in the provided information
        - If database info is empty or says "no data", say "I don't have that information" rather than guessing
        - If policy info is missing, don't make up return/exchange rules or terms
        - It's always better to say "I'm not sure" or "I don't have that information" than to be confidently wrong
        - Do not mention internal systems, databases, or technical processes

        Response guidelines:
        - Don't start with "Based on..." or "According to..."  
        - Don't list information in bullet points unless specifically asked
        - Speak as if you're knowledgeable about both products and policies
        - If combining product and policy info, do it seamlessly
        - For general questions unrelated to products/policies, be helpful and conversational
        - Reference previous conversation naturally when it adds value

        Generate a natural, helpful response:
        """
    )
    
    best_response = ""
    
    for iteration in range(max_iterations):
        # Generate candidate response
        formatted_prompt = conversation_prompt.format_messages(
            user_query=user_query,
            previous_context=previous_context or "No previous conversation",
            db_output=db_output or "No specific product information available",
            policy_output=policy_output or "No specific policy information available"
        )
        
        try:
            candidate_response = llm.invoke(formatted_prompt).content.strip()
        except Exception as e:
            return _generate_fallback_response(user_query)
        
        best_response = candidate_response
        
        # Use rule-based quality check instead of LLM evaluation
        if _is_response_high_quality(candidate_response, user_query):
            break
    
    # Final safety check - ensure we have a valid response
    if not best_response or len(best_response.strip()) < 10:
        best_response = _generate_fallback_response(user_query)
    
    return best_response

def update_conversation_context(
    previous_context: str, 
    user_query: str, 
    agent_response: str, 
    max_tokens: int = 300
):
    """
    Helper function to maintain conversation context efficiently.
    Uses rough token estimation (1 token ≈ 4 characters) to manage length.
    """
    new_exchange = f"User: {user_query}\nAssistant: {agent_response}\n"
    
    if not previous_context:
        updated_context = new_exchange
    else:
        updated_context = previous_context.strip() + "\n" + new_exchange
    
    # Trim context if too long (keep most recent exchanges)
    # Rough estimate: 1 token ≈ 4 characters for English text
    max_chars = max_tokens * 4
    while len(updated_context) > max_chars and "\n" in updated_context:
        lines = updated_context.split('\n')
        if len(lines) > 2:
            # Remove the oldest exchange (first 2 lines: User + Assistant)
            updated_context = '\n'.join(lines[2:])
        else:
            # Keep at least the most recent exchange
            break
    
    return updated_context.strip()

__all__ = ["reflection_agent", "update_conversation_context"]