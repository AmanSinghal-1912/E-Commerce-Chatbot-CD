import os
import sys
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from policy.agent import policy_agent
from realtime_db_agent.agent import db_agent
from reflection_agent.agent import reflection_agent

# Load environment variables
load_dotenv()

# Initialize the routing LLM
llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.1-8b-instant",  # lightweight model for routing
    temperature=0.1
)

def determine_agent(query: str) -> str:
    """Determine which sub-agent(s) should handle the query."""
    prompt = HumanMessage(content=f"""
    Determine which type of information is needed to answer this query:
    
    "{query}"
    
    Return ONLY one of these options:
    - "policy" (for company policies only)
    - "database" (for product information only)
    - "both" (when both policy and product information are needed)
    """)
    
    response = llm.invoke([prompt])
    agent_type = response.content.strip().lower()
    
    # Validate response
    if agent_type not in ["policy", "database", "both"]:
        agent_type = "both"  # Default to using both if unclear
        
    return agent_type

def head_agent(query: str, previous_context: str = "") -> str:
    """Main agent that routes queries to appropriate sub-agents."""
    try:
        # Step 1: Determine which agent(s) to use
        agent_type = determine_agent(query)
        
        # Step 2: Get responses from appropriate agent(s)
        if agent_type == "database":
            db_output = db_agent(query)
            policy_output = ""
        elif agent_type == "policy":
            db_output = ""
            policy_output = policy_agent(query)
        else:  # both
            db_output = db_agent(query)
            policy_output = policy_agent(query)
        
        # Step 3: Use reflection agent to refine the response
        # Pass user query as context so it can detect intent like
        # "why should I buy this?" and generate one-liners
        final_response = reflection_agent(
            db_output=db_output,
            policy_output=policy_output,
            previous_context=query if not previous_context else previous_context + " " + query
        )
        
        return final_response
    except Exception as e:
        return f"I'm not sure how to answer that. Could you rephrase your question?"

if __name__ == "__main__":
    print("Welcome! I can help with policy questions and product information.")
    context = ""  # keep running context across turns
    
    while True:
        user_query = input("\nYour question (type 'exit' to quit): ")
        if user_query.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break
            
        response = head_agent(user_query, previous_context=context)
        print("\nResponse:", response)
        
        # Update context for next turn
        context += " " + user_query
