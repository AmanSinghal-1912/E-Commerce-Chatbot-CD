import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
load_dotenv()

# Define the persistent directory
current_dir = os.path.dirname(os.path.abspath(__file__))
persistent_directory = os.path.join(current_dir, "db", "chroma_db")

# Define the embedding model
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Load the existing vector store with the embedding function
db = Chroma(persist_directory=persistent_directory,
            embedding_function=embeddings)

# Define the user's question
query = "i have got a damaged product, what can be done now?"

# Retrieve relevant documents based on the query
retriever = db.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 2}, 
)

relevant_docs = retriever.invoke(query)

# Display the relevant results with metadata
print("\n--- Relevant Documents ---")
retrieved_context = ""
for i, doc in enumerate(relevant_docs, 1):
    print(f"Document {i}:\n{doc.page_content}\n")
    retrieved_context += doc.page_content + "\n\n"
    if doc.metadata:
        print(f"Source: {doc.metadata.get('source', 'Unknown')}\n")

# Initialize the LLM
llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.1-8b-instant",
    temperature=0.1
)

# Create prompt with retrieved documents and query
prompt = HumanMessage(content=f"""
Based on our company policies, please answer the following customer query:

Customer Question: {query}

Relevant Policy Information:
{retrieved_context}

Please provide a concise, helpful response that directly answers the customer's question
using only the information in our policy documents. If the information needed is not 
available in the provided policy excerpts, acknowledge this and suggest the next steps.
""")

# Get refined answer from LLM
response = llm.invoke([prompt])

print("\n--- LLM Response ---")
print(response.content)

