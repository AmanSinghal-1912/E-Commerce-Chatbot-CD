from langchain.tools import Tool
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Set up persistent directory (go up one level from tools/)
current_dir = os.path.dirname(os.path.abspath(__file__))
persistent_directory = os.path.join(current_dir, "..", "db", "chroma_db")
persistent_directory = os.path.normpath(persistent_directory)

# Load embeddings + DB
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
db = Chroma(persist_directory=persistent_directory, embedding_function=embeddings)

# Create retriever
retriever = db.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 2}
)

# Initialize LLM
llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.1-8b-instant",
    temperature=0.1
)

# Define the tool function with LLM enhancement
def policy_lookup(query: str) -> str:
    """Look up policy information and generate a refined answer."""
    # Step 1: Retrieve relevant docs
    docs = retriever.invoke(query)
    
    # Step 2: If no docs found, return early
    if not docs:
        return "I couldn't find any relevant policy information to answer your question."
    
    # Step 3: Extract context from docs
    retrieved_context = "\n\n".join([doc.page_content for doc in docs])
    
    # Step 4: Generate refined response with LLM
    prompt = HumanMessage(content=f"""
    Based on our company policies, please answer the following customer query:

    Customer Question: {query}

    Relevant Policy Information:
    {retrieved_context}

    Please provide a concise, helpful response that directly answers the customer's question
    using only the information in our policy documents. If the information needed is not 
    available in the provided policy excerpts, acknowledge this and suggest the next steps.
    """)
    
    try:
        response = llm.invoke([prompt])
        return response.content
    except Exception as e:
        # Fallback to raw context if LLM fails
        return f"Based on our policies: {retrieved_context}"

# Wrap as a LangChain Tool
policy_tool = Tool(
    name="PolicyAgentTool",
    func=policy_lookup,
    description="Look up company policies and generate answers to customer queries."
)

__all__ = ["policy_tool"]
