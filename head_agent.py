import os
import sys
from dotenv import load_dotenv
from openai import OpenAI
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from policy.agent import policy_agent
from realtime_db_agent.agent import db_agent
from reflection_agent.agent import reflection_agent, update_conversation_context

# Load environment variables
load_dotenv()

# Initialize LLMs
client = OpenAI(
    base_url="https://api.studio.nebius.com/v1/",
    api_key=os.environ.get("NEBIUS_API_KEY")
)

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.3-70b-versatile",
    temperature=0.2
)

class HeadAgent:
    def __init__(self):
        self.conversation_context = ""
    
    def determine_agent(self, query: str) -> str:
        """Determine which sub-agent(s) should handle the query."""
        prompt = f"""
        Analyze this user query and determine what type of information is needed:
        
        User Query: "{query}"
        
        Categories:
        - "policy" - Questions about warranties, returns, shipping, company policies, terms of service
        - "database" - Questions about specific products, pricing, availability, product details, inventory
        - "both" - Questions that need both product info AND policy info (like "what's the warranty on iPhone 13?")
        - "general" - Greetings, general chat, questions not related to products or policies
        
        Examples:
        - "What is your return policy?" → policy
        - "Do you have iPhone 13?" → database  
        - "What's the warranty on MacBook Pro?" → both
        - "Hello" → general
        - "How are you?" → general
        
        Return ONLY one word: policy, database, both, or general
        """
        
        try:
            response = llm.invoke([HumanMessage(content=prompt)])
            agent_type = response.content.strip().lower()
            
            # Validate response
            if agent_type not in ["policy", "database", "both", "general"]:
                agent_type = "general"  # Safe default
                
            print(f"[DEBUG] Query classified as: {agent_type}")
            return agent_type
            
        except Exception as e:
            print(f"[DEBUG] Classification error: {e}")
            return "general"
    
    def get_agent_responses(self, query: str, agent_type: str):
        """Get responses from the appropriate agents based on classification."""
        db_output = ""
        policy_output = ""
        
        try:
            if agent_type == "database":
                print("[DEBUG] Querying Database Agent only...")
                db_output = db_agent(query)
                
            elif agent_type == "policy":
                print("[DEBUG] Querying Policy Agent only...")
                policy_output = policy_agent(query)
                
            elif agent_type == "both":
                print("[DEBUG] Querying both Database and Policy Agents...")
                db_output = db_agent(query)
                policy_output = policy_agent(query)
                
            # For "general" queries, we don't query any specific agents
            # The reflection agent will handle general conversation
            
        except Exception as e:
            print(f"[DEBUG] Agent query error: {e}")
        
        return db_output, policy_output
    
    def process_query(self, query: str) -> str:
        """Main method to process any user query."""
        if not query or query.strip() == "":
            return "I'm here to help! Please ask me anything about our products or policies."
        
        try:
            # Step 1: Determine which agents to use
            agent_type = self.determine_agent(query)
            
            # Step 2: Get responses from appropriate agents
            db_output, policy_output = self.get_agent_responses(query, agent_type)
            
            print(f"[DEBUG] DB Output: {db_output[:100]}..." if db_output else "[DEBUG] No DB output")
            print(f"[DEBUG] Policy Output: {policy_output[:100]}..." if policy_output else "[DEBUG] No Policy output")
            
            # Step 3: Use reflection agent to synthesize final response
            print("[DEBUG] Generating final response with Reflection Agent...")
            final_response = reflection_agent(
                db_output=db_output,
                policy_output=policy_output,
                previous_context=self.conversation_context,
                user_query=query  # This was missing in the original!
            )
            
            # Step 4: Update conversation context for future interactions
            self.conversation_context = update_conversation_context(
                self.conversation_context,
                query,
                final_response
            )
            
            return final_response
            
        except Exception as e:
            print(f"[ERROR] Processing failed: {e}")
            return "I apologize, but I'm having trouble processing your request right now. Could you please try rephrasing your question?"

def main():
    agent = HeadAgent()
    print("🤖 Hello! I'm your AI assistant. I can help you with:")
    print("   • Product information and availability")
    print("   • Company policies (warranty, returns, shipping)")
    print("   • General questions and conversation")
    print("   • Just ask me anything!\n")
    
    while True:
        try:
            query = input("You: ").strip()
            
            if query.lower() in ['exit', 'quit', 'bye', 'goodbye']:
                print("Assistant: Thank you for chatting! Have a wonderful day! 👋")
                break
                
            if not query:
                print("Assistant: I'm listening! What would you like to know?")
                continue
            
            print("Assistant: ", end="", flush=True)
            response = agent.process_query(query)
            print(response)
            print("-" * 50)
            
        except KeyboardInterrupt:
            print("\nAssistant: Goodbye! Have a great day! 👋")
            break
        except Exception as e:
            print(f"Assistant: I encountered an error: {e}")

if __name__ == "__main__":
    main()
