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

def reflection_agent(db_output: str = "", policy_output: str = "", previous_context: str = "", user_query: str = "", max_iterations: int = 2):
    """
    Synthesizes responses from DB and Policy agents into natural, conversational responses.
    Handles context awareness and general conversation naturally.
    """
    
    # Main conversation prompt
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
        
        candidate_response = llm.invoke(formatted_prompt).content.strip()
        
        # Quality check prompt
        quality_check_prompt = f"""
        Evaluate this customer service response for naturalness and helpfulness:

        User Query: "{user_query}"
        Response: "{candidate_response}"

        Check if the response:
        1. Sounds conversational and human-like (not robotic or templated)
        2. Appropriately addresses the user's question
        3. Is the right length (not too short/brief, not too long/overwhelming)
        4. Flows naturally from any previous context
        5. Integrates available information smoothly

        Rate this response: EXCELLENT, GOOD, or NEEDS_IMPROVEMENT
        Only respond with one of these three ratings.
        """
        
        quality_rating = llm.invoke(quality_check_prompt).content.strip().upper()
        
        best_response = candidate_response
        
        # Accept if good quality, or if we've reached max iterations
        if "EXCELLENT" in quality_rating or "GOOD" in quality_rating or iteration == max_iterations - 1:
            break
    
    # Final safety check - ensure we have a response
    if not best_response or len(best_response.strip()) < 10:
        fallback_prompt = f"""
        The user asked: "{user_query}"
        
        Provide a brief, helpful response. If you can't answer specifically, politely explain what you can help with instead.
        Keep it conversational and friendly.
        """
        best_response = llm.invoke(fallback_prompt).content.strip()
    
    return best_response

# Context management helper
def update_conversation_context(previous_context: str, user_query: str, agent_response: str, max_context_length: int = 800):
    """
    Helper function to maintain conversation context efficiently
    """
    new_exchange = f"User: {user_query}\nAssistant: {agent_response}\n"
    
    if not previous_context:
        return new_exchange
    
    updated_context = previous_context + "\n" + new_exchange
    
    # Trim context if too long (keep most recent exchanges)
    if len(updated_context) > max_context_length:
        lines = updated_context.split('\n')
        # Keep last few exchanges (each exchange is typically 2 lines)
        recent_lines = lines[-(max_context_length//50):]  # Approximate line count
        updated_context = '\n'.join(recent_lines)
    
    return updated_context

__all__ = ["reflection_agent", "update_conversation_context"]
