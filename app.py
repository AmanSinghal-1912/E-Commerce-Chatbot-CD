import streamlit as st
from head_agent import HeadAgent

# --- Inject your luxury CSS theme ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Crimson+Text:ital,wght@0,400;0,600;1,400&family=Playfair+Display:wght@400;500;600;700&display=swap');

/* 🎨 Global App - Luxury E-commerce Vibe */
.stApp {
    background: 
        radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
        radial-gradient(circle at 80% 20%, rgba(255, 119, 198, 0.15) 0%, transparent 50%),
        linear-gradient(135deg, #0a0a0f 0%, #1a1625 25%, #2d2438 50%, #1a1625 75%, #0a0a0f 100%);
    color: #e8e6f0;
    font-family: 'Crimson Text', 'Times New Roman', Georgia, serif;
    font-size: 17px;
    line-height: 1.8;
    min-height: 100vh;
    position: relative;
}

/* ✨ Animated Background Particles */
.stApp::before {
    content: "";
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-image: 
        radial-gradient(2px 2px at 20px 30px, rgba(255,255,255,0.15), transparent),
        radial-gradient(2px 2px at 40px 70px, rgba(255,255,255,0.1), transparent),
        radial-gradient(1px 1px at 90px 40px, rgba(255,255,255,0.1), transparent),
        radial-gradient(1px 1px at 130px 80px, rgba(255,255,255,0.1), transparent);
    background-size: 200px 100px;
    animation: sparkle 20s linear infinite;
    pointer-events: none;
    z-index: -1;
}

@keyframes sparkle {
    from { transform: translateY(0px); }
    to { transform: translateY(-200px); }
}

/* 🏷 Majestic Title */
h1 {
    font-family: 'Playfair Display', 'Times New Roman', serif !important;
    color: #f8f6ff !important;
    font-size: 3.5rem !important;
    font-weight: 700 !important;
    text-align: center;
    margin: 2rem 0 3rem 0 !important;
    text-shadow: 
        0 0 20px rgba(120, 119, 198, 0.5),
        0 0 40px rgba(120, 119, 198, 0.3),
        0 5px 10px rgba(0,0,0,0.8);
    letter-spacing: -0.02em;
    position: relative;
    background: linear-gradient(135deg, #f8f6ff 0%, #e0d9ff 50%, #c4b5fd 100%);
    background-clip: text;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: titleGlow 4s ease-in-out infinite alternate;
}

@keyframes titleGlow {
    from { text-shadow: 0 0 20px rgba(120, 119, 198, 0.3); }
    to { text-shadow: 0 0 30px rgba(120, 119, 198, 0.6), 0 0 40px rgba(255, 119, 198, 0.2); }
}

h1::after {
    content: "";
    position: absolute;
    bottom: -15px;
    left: 50%;
    transform: translateX(-50%);
    width: 120px;
    height: 4px;
    background: linear-gradient(90deg, transparent 0%, #c4b5fd 20%, #7c77c6 50%, #ff77c6 80%, transparent 100%);
    border-radius: 2px;
    animation: lineGlow 3s ease-in-out infinite alternate;
}

@keyframes lineGlow {
    from { box-shadow: 0 0 10px rgba(120, 119, 198, 0.3); }
    to { box-shadow: 0 0 20px rgba(120, 119, 198, 0.8); }
}

/* 💬 Premium Chat Messages */
.stChatMessage {
    padding: 24px 28px;
    margin: 20px 0;
    border-radius: 20px;
    font-size: 16px;
    line-height: 1.8;
    font-family: 'Crimson Text', 'Times New Roman', serif;
    position: relative;
    backdrop-filter: blur(15px);
    animation: messageSlide 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

@keyframes messageSlide {
    from { 
        opacity: 0; 
        transform: translateY(30px) scale(0.9); 
        filter: blur(5px);
    }
    to { 
        opacity: 1; 
        transform: translateY(0) scale(1); 
        filter: blur(0px);
    }
}

.stChatMessage:hover {
    transform: translateY(-3px) scale(1.01);
}

/*  User Message - Luxury Shopping Experience */
.stChatMessage[data-testid*="user"] {
    background: linear-gradient(135deg, 
        rgba(248, 246, 255, 0.95) 0%, 
        rgba(224, 217, 255, 0.9) 50%, 
        rgba(196, 181, 253, 0.85) 100%);
    color: #2d1b69;
    margin-left: 15%;
    margin-right: 5%;
    border: 1px solid rgba(196, 181, 253, 0.3);
    box-shadow: 
        0 10px 40px rgba(120, 119, 198, 0.15),
        inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.stChatMessage[data-testid*="user"]::before {
    content: "🛍️";
    position: absolute;
    top: -8px;
    right: 15px;
    font-size: 1.2rem;
    background: linear-gradient(135deg, #c4b5fd, #7c77c6);
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 15px rgba(120, 119, 198, 0.3);
    animation: iconBounce 2s ease-in-out infinite;
}

/* 🤖 Assistant Message - AI Concierge Style */
.stChatMessage[data-testid*="assistant"] {
    background: linear-gradient(135deg, 
        rgba(26, 22, 37, 0.95) 0%, 
        rgba(45, 36, 56, 0.9) 50%, 
        rgba(120, 119, 198, 0.1) 100%);
    color: #e8e6f0;
    margin-right: 15%;
    margin-left: 5%;
    border: 1px solid rgba(120, 119, 198, 0.3);
    box-shadow: 
        0 10px 40px rgba(0, 0, 0, 0.3),
        0 0 20px rgba(120, 119, 198, 0.1),
        inset 0 1px 0 rgba(255, 255, 255, 0.05);
}

.stChatMessage[data-testid*="assistant"]::before {
    content: "🎭";
    position: absolute;
    top: -8px;
    left: 15px;
    font-size: 1.2rem;
    background: linear-gradient(135deg, #7c77c6, #ff77c6);
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 15px rgba(255, 119, 198, 0.3);
    animation: iconGlow 3s ease-in-out infinite alternate;
}

@keyframes iconBounce {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-5px); }
}

@keyframes iconGlow {
    from { box-shadow: 0 4px 15px rgba(255, 119, 198, 0.3); }
    to { box-shadow: 0 4px 25px rgba(255, 119, 198, 0.6); }
}

/* 🏷️ Elegant Message Labels */
.stChatMessage [data-testid="stChatMessageContent"]::before {
    display: block;
    font-family: 'Playfair Display', serif;
    font-size: 0.8rem;
    font-weight: 600;
    margin-bottom: 12px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    opacity: 0.9;
}

.stChatMessage[data-testid*="user"] [data-testid="stChatMessageContent"]::before {
    content: "✨ You";
    color: #6d28d9;
    text-shadow: 0 1px 3px rgba(109, 40, 217, 0.3);
}

.stChatMessage[data-testid*="assistant"] [data-testid="stChatMessageContent"]::before {
    content: "🤖 Personal Shopping Assistant";
    color: #c4b5fd;
    text-shadow: 0 1px 3px rgba(196, 181, 253, 0.3);
}

/* 🖋 Luxurious Input Design */
.stChatInputContainer {
    background: linear-gradient(135deg, 
        rgba(26, 22, 37, 0.9) 0%, 
        rgba(45, 36, 56, 0.85) 100%);
    backdrop-filter: blur(20px);
    border-radius: 25px;
    padding: 20px;
    margin: 25px 0;
    border: 2px solid rgba(196, 181, 253, 0.2);
    box-shadow: 
        0 15px 50px rgba(0,0,0,0.3),
        0 0 30px rgba(120, 119, 198, 0.1),
        inset 0 1px 0 rgba(255,255,255,0.05);
    position: relative;
    overflow: hidden;
}

.stChatInputContainer::before {
    content: "";
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent 0%, rgba(196, 181, 253, 0.1) 50%, transparent 100%);
    animation: shimmer 3s ease-in-out infinite;
}

@keyframes shimmer {
    0% { left: -100%; }
    100% { left: 100%; }
}

.stTextInput > div > div > input {
    background: rgba(248, 246, 255, 0.95) !important;
    color: #2d1b69 !important;
    border: 2px solid rgba(196, 181, 253, 0.3) !important;
    border-radius: 18px !important;
    padding: 18px 24px !important;
    font-size: 16px !important;
    font-family: 'Crimson Text', 'Times New Roman', serif !important;
    font-weight: 400 !important;
    transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94) !important;
    box-shadow: 
        inset 0 2px 8px rgba(120, 119, 198, 0.1),
        0 0 0 0 rgba(196, 181, 253, 0) !important;
}

.stTextInput > div > div > input::placeholder {
    color: rgba(45, 27, 105, 0.6) !important;
    font-style: italic;
}

.stTextInput > div > div > input:focus {
    border: 2px solid #7c77c6 !important;
    background: rgba(255, 255, 255, 0.98) !important;
    box-shadow: 
        inset 0 2px 8px rgba(120, 119, 198, 0.1),
        0 0 0 4px rgba(196, 181, 253, 0.2),
        0 10px 30px rgba(120, 119, 198, 0.2) !important;
    outline: none !important;
    transform: translateY(-1px);
}

/* Sophisticated Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, 
        rgba(10, 10, 15, 0.95) 0%, 
        rgba(26, 22, 37, 0.9) 50%, 
        rgba(45, 36, 56, 0.85) 100%);
    backdrop-filter: blur(15px);
    border-right: 2px solid rgba(196, 181, 253, 0.1);
    color: #e8e6f0;
}

[data-testid="stSidebar"] > div {
    padding: 2rem 1rem;
}

[data-testid="stSidebar"] h1, 
[data-testid="stSidebar"] h2, 
[data-testid="stSidebar"] h3 {
    font-family: 'Playfair Display', serif !important;
    color: #c4b5fd !important;
    font-weight: 600 !important;
    text-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

/* ⚡ Premium Status Bar */
#status-bar {
    background: linear-gradient(135deg, 
        #7c77c6 0%, 
        #c4b5fd 25%, 
        #ff77c6 75%, 
        #7c77c6 100%);
    color: white;
    font-family: 'Playfair Display', serif;
    font-weight: 600;
    padding: 20px 28px;
    border-radius: 16px;
    margin: 30px 0;
    text-align: center;
    font-size: 1rem;
    box-shadow: 
        0 10px 30px rgba(120, 119, 198, 0.4),
        0 0 20px rgba(255, 119, 198, 0.2),
        inset 0 1px 0 rgba(255,255,255,0.2);
    text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    border: 1px solid rgba(255,255,255,0.1);
    animation: statusPulse 4s ease-in-out infinite;
    position: relative;
    overflow: hidden;
}

@keyframes statusPulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.02); }
}

#status-bar::before {
    content: " ";
    position: absolute;
    left: 20px;
    top: 50%;
    transform: translateY(-50%);
    font-size: 1.2rem;
    animation: diamondSpin 6s linear infinite;
}

@keyframes diamondSpin {
    from { transform: translateY(-50%) rotate(0deg); }
    to { transform: translateY(-50%) rotate(360deg); }
}

/* 🎨 Enhanced Code Styling */
.stChatMessage code {
    background: rgba(196, 181, 253, 0.15);
    color: #c4b5fd;
    padding: 3px 8px;
    border-radius: 6px;
    font-family: 'SF Mono', 'Monaco', 'Cascadia Code', monospace;
    font-size: 0.9em;
    border: 1px solid rgba(196, 181, 253, 0.2);
}

.stChatMessage pre {
    background: rgba(26, 22, 37, 0.8);
    color: #e8e6f0;
    padding: 16px 20px;
    border-radius: 12px;
    border-left: 4px solid #7c77c6;
    overflow-x: auto;
    backdrop-filter: blur(10px);
    box-shadow: inset 0 2px 8px rgba(0,0,0,0.3);
}

/* ✨ Premium Scrollbar */
::-webkit-scrollbar {
    width: 12px;
}

::-webkit-scrollbar-track {
    background: rgba(26, 22, 37, 0.3);
    border-radius: 6px;
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, #7c77c6, #c4b5fd);
    border-radius: 6px;
    border: 2px solid rgba(26, 22, 37, 0.3);
}

::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(135deg, #c4b5fd, #ff77c6);
    box-shadow: 0 0 10px rgba(196, 181, 253, 0.3);
}

/* 📱 Mobile Responsiveness */
@media (max-width: 768px) {
    .stChatMessage[data-testid*="user"] {
        margin-left: 8%;
        margin-right: 2%;
    }
    
    .stChatMessage[data-testid*="assistant"] {
        margin-right: 8%;
        margin-left: 2%;
    }
    
    h1 {
        font-size: 2.8rem !important;
        margin: 1rem 0 2rem 0 !important;
    }
    
    .stChatMessage {
        padding: 18px 20px;
        margin: 15px 0;
        font-size: 15px;
    }
    
    .stChatInputContainer {
        padding: 15px;
        margin: 20px 0;
    }
}
</style>
""", unsafe_allow_html=True)

# --- App title ---
st.markdown("<h1>✨ Your AI Shopping Assistant</h1>", unsafe_allow_html=True)

# --- Session State for conversation persistence ---
if "agent" not in st.session_state:
    st.session_state.agent = HeadAgent()
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Show conversation history ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- User input box ---
if query := st.chat_input("Ask me about products, policies, or just say hi..."):
    # Display user message
    st.chat_message("user").markdown(query)
    st.session_state.messages.append({"role": "user", "content": query})

    # Get assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = st.session_state.agent.process_query(query)
            st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})

# --- Optional status bar ---
st.markdown("""
<div id="status-bar">
  Connected to AI Assistant • Ready to assist
</div>
""", unsafe_allow_html=True)
