import streamlit as st
import json
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import time

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="AI Novelist Studio", layout="wide")

st.title("📚 AI Novelist Studio")
st.markdown("### From Premise to Polished Prose")

# --- SIDEBAR: CONFIGURATION ---
with st.sidebar:
    st.header("⚙️ Mission Config")
    
    # API Key Input (Secure handling)
    api_key = st.text_input("OpenAI API Key", type="password")
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
    
    st.divider()
    
    # Story Variables
    genre = st.selectbox("Genre", ["Techno-Thriller", "Cyberpunk", "High Fantasy", "Romance"])
    tone = st.select_slider("Tone Intensity", options=["Light", "Balanced", "Gritty", "Dark"])
    style = st.text_input("Author Style", value="Hemingway-esque brevity")
    
    # Reset Button
    if st.button("Clear Session Memory"):
        st.session_state.clear()
        st.rerun()

# --- SESSION STATE MANAGEMENT ---
# Streamlit re-runs the script on every click. 
# We use session_state to remember data between clicks.

if 'story_bible' not in st.session_state:
    st.session_state['story_bible'] = {
        "characters": {},
        "summary": "Start of the story."
    }
if 'scene_card' not in st.session_state:
    st.session_state['scene_card'] = ""
if 'draft' not in st.session_state:
    st.session_state['draft'] = ""
if 'report' not in st.session_state:
    st.session_state['report'] = ""

# --- LLM SETUP (The Brain) ---
# Only initialize if API key is present
llm = None
if api_key:
    llm = ChatOpenAI(model="gpt-4-turbo", temperature=0.7)

# --- THE PROMPTS (Simplified for the App) ---
# In a real app, these would be the full system prompts we designed earlier.
# --- MOCK FUNCTIONS ---

def generate_outline(premise, genre, context):
    time.sleep(2) # Simulate AI thinking for 2 seconds
    return f"""{{
    "title": "Mock Outline for {genre}",
    "beats": [
        "1. {premise} (The Setup)",
        "2. The protagonist faces a glitch in the system.",
        "3. A sudden betrayal occurs.",
        "4. Cliffhanger ending."
    ]
}}"""

def write_draft(scene_card, style):
    time.sleep(3) # Simulate writing
    return f"""
    The neon lights of the server room hummed with a headache-inducing buzz. 
    This was the style of {style}—short, punchy, no nonsense.
    
    "System breach," the console read.
    
    He didn't panic. He never panicked. He just typed faster, his fingers blurring like hummingbirds against the mechanical keys.
    (This is a mock draft generated based on: {scene_card})
    """

def critique_draft(draft, genre):
    time.sleep(2) # Simulate reading
    return f"""
    # Editorial Report
    * **Genre Compliance:** {genre} conventions are met.
    * **Pacing:** Good, but the middle section drags.
    * **Logic Check:** Why did the console buzz? Servers are usually silent.
    """

# --- UI COLUMN LAYOUT ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Step 1: The Blueprint")
    premise_input = st.text_area("Enter Chapter Premise:", height=100, placeholder="e.g., Jinx hacks the mainframe but triggers a trap.")
    
    if st.button("🏗️ Generate Outline"):
        with st.spinner("Architect is thinking..."):
            # Pass the Memory (Story Bible) to the Outline
            bible_context = json.dumps(st.session_state['story_bible'])
            st.session_state['scene_card'] = generate_outline(premise_input, genre, bible_context)
            st.rerun()

    # HUMAN-IN-THE-LOOP: Editable Text Area
    # The user can edit the AI's outline before the Writer sees it.
    if st.session_state['scene_card']:
        st.info("Edit the outline below if needed, then click 'Write Draft'.")
        edited_card = st.text_area("Scene Card (JSON/XML)", value=st.session_state['scene_card'], height=300)
        st.session_state['scene_card'] = edited_card

        if st.button("✍️ Write Draft"):
            with st.spinner("Drafter is writing..."):
                st.session_state['draft'] = write_draft(st.session_state['scene_card'], style)
                st.rerun()

with col2:
    st.subheader("Step 2: The Manuscript")
    
    if st.session_state['draft']:
        st.success("Draft Generated!")
        st.text_area("Final Prose", value=st.session_state['draft'], height=400)
        
        if st.button("🧐 Analyze & Edit"):
            with st.spinner("Editor is reviewing..."):
                st.session_state['report'] = critique_draft(st.session_state['draft'], genre)
                
                # Mock Archivist Update (In real app, use LLM here)
                st.session_state['story_bible']['summary'] += f" -> Processed premise: {premise_input}"
                st.rerun()

    # Display Editorial Report if available
    if st.session_state['report']:
        with st.expander("View Editorial Report"):
            st.markdown(st.session_state['report'])
        
        with st.expander("View Story Bible (Memory)"):
            st.json(st.session_state['story_bible'])

# --- FOOTER ---
st.markdown("---")
st.caption("Powered by LangChain & Streamlit. Designed by The Prompt Engineer Master.")
