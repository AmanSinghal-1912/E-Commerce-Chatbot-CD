from openai import OpenAI
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os
import difflib
import re

load_dotenv()

# Initialize Nebius client
client = OpenAI(
    base_url="https://api.studio.nebius.com/v1/",
    api_key=os.environ.get("NEBIUS_API_KEY")
)

def reflection_agent(db_output: str, policy_output: str, max_iterations: int = 2):
    """
    Combines DB + Policy outputs into a user-friendly final response.
    Handles deduplication automatically.
    """
    if not db_output and not policy_output:
        return "Hello! I can help with product information and company policies. What would you like to know?"
    
    prompt = f"""
    Combine the following information into a helpful response:
    
    Database information: {db_output}
    Policy information: {policy_output}
    
    IMPORTANT GUIDELINES:
    - NO REPETITION - present each fact exactly once
    - Be concise and direct
    - Use numbered lists for multiple similar items
    - Maximum 150 words
    - Bold important facts with **asterisks**
    """

    response = client.chat.completions.create(
        model="Qwen/Qwen3-Coder-480B-A35B-Instruct",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that provides clear, concise responses without repetition."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )
    
    # Extract content from response
    response_text = response.choices[0].message.content
    
    # Apply deduplication
    response_text = remove_repetition(response_text)
    
    return response_text

def remove_repetition(text):
    """Remove repeated sentences and paragraphs."""
    if not text:
        return ""
        
    # Split into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    unique_sentences = []
    seen_sentences = set()
    
    for sentence in sentences:
        # Normalize for comparison
        normalized = re.sub(r'\s+', ' ', sentence.lower().strip())
        if len(normalized) < 10:  # Skip very short sentences
            unique_sentences.append(sentence)
            continue
            
        # Check if very similar to any existing sentence
        if not any(difflib.SequenceMatcher(None, normalized, seen).ratio() > 0.7 for seen in seen_sentences):
            seen_sentences.add(normalized)
            unique_sentences.append(sentence)
    
    # Rejoin sentences
    result = ' '.join(unique_sentences)
    
    # Fix any broken markdown formatting
    result = re.sub(r'\*\*([^*]+)(?!\*\*)', r'**\1**', result)
    
    return result

__all__ = ["reflection_agent"]
