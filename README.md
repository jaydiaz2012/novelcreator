# CLAUDE.md — AI Novelist Studio

This file provides guidance for AI assistants (Claude, Copilot, etc.) working in this repository.

---

## Project Overview

**novelcreator** is a single-file Python web application called **AI Novelist Studio**. It provides a browser-based interface for AI-assisted creative writing using a multi-stage pipeline: premise → outline → draft → editorial critique.

The application is a prototype/MVP. The LLM integration scaffolding is in place (LangChain + OpenAI), but the three core generation functions are currently **mocked** with `time.sleep()` placeholders returning hardcoded strings.

---

## Repository Structure

```
novelcreator/
├── app.py            # Entire application — single entry point
├── requirements.txt  # Python dependencies
├── README.md         # Project title only (minimal)
└── LICENSE           # MIT License
```

There are no subdirectories, no packages, no test files, and no CI/CD configuration. All application logic lives in `app.py`.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.x |
| Web UI | [Streamlit](https://streamlit.io/) |
| LLM Orchestration | [LangChain](https://python.langchain.com/) |
| LLM Provider | OpenAI (`gpt-4-turbo`) |
| OpenAI Client | `langchain-openai`, `openai` |
| Env Config | `python-dotenv` |

---

## Running the Application

### Install dependencies

```bash
pip install -r requirements.txt
```

### Start the app

```bash
streamlit run app.py
```

The app runs on `http://localhost:8501` by default.

### API key

The OpenAI API key is entered via the sidebar UI at runtime (password field). It is written to `os.environ["OPENAI_API_KEY"]` directly. There is no `.env` file in the repo — the key is never persisted to disk.

---

## Application Architecture

### Session State

Streamlit re-executes the entire script on every user interaction. Persistent state is stored in `st.session_state` using these keys:

| Key | Type | Purpose |
|---|---|---|
| `story_bible` | `dict` | Tracks characters and running plot summary across chapters |
| `scene_card` | `str` | The current outline/scene structure (editable by the user) |
| `draft` | `str` | Generated prose for the current chapter |
| `report` | `str` | Editorial critique of the current draft |

The sidebar "Clear Session Memory" button calls `st.session_state.clear()` and `st.rerun()` to reset everything.

### UI Layout

Two equal-width columns (`st.columns([1, 1])`):

**Column 1 — The Blueprint**
1. `premise_input`: user enters a chapter premise
2. "Generate Outline" button → calls `generate_outline()` → stores result in `session_state['scene_card']`
3. Editable `st.text_area` for the scene card (human-in-the-loop step)
4. "Write Draft" button → calls `write_draft()` → stores result in `session_state['draft']`

**Column 2 — The Manuscript**
1. Displays the draft if present
2. "Analyze & Edit" button → calls `critique_draft()` → stores result in `session_state['report']`; also appends to the story bible summary
3. Collapsible expanders for the editorial report and the story bible JSON

### LLM Initialization

```python
llm = None
if api_key:
    llm = ChatOpenAI(model="gpt-4-turbo", temperature=0.7)
```

The `llm` object is created conditionally. The three generation functions currently **do not use it** — they are mocks. Real LangChain chains would be built using `ChatPromptTemplate | llm | StrOutputParser()`.

---

## Core Functions

All three functions are currently mocked. Their signatures and expected behavior define the integration contract:

### `generate_outline(premise, genre, context) -> str`

- **Inputs:** chapter premise (string), genre (string), story bible JSON (string)
- **Expected output:** JSON string with `"title"` and `"beats"` keys
- **Mock:** returns a hardcoded JSON template after a 2-second sleep

### `write_draft(scene_card, style) -> str`

- **Inputs:** scene card text (the outline, possibly edited by user), author style string
- **Expected output:** narrative prose for the chapter
- **Mock:** returns a fixed paragraph after a 3-second sleep

### `critique_draft(draft, genre) -> str`

- **Inputs:** draft prose (string), genre (string)
- **Expected output:** Markdown-formatted editorial report covering genre compliance, pacing, and logic
- **Mock:** returns a hardcoded bullet-point report after a 2-second sleep

---

## Conventions

- **Language:** Python; snake_case for all identifiers
- **UI text:** Uses emoji in titles, buttons, and section headers (`📚`, `⚙️`, `🏗️`, `✍️`, `🧐`)
- **Section comments:** Major sections separated by `# --- SECTION NAME ---`
- **No classes:** The app is entirely procedural/functional; no OOP
- **No environment file:** API key is never written to disk; always passed via UI
- **No type hints:** Functions have no annotations
- **No tests:** No test framework is configured

---

## Key Development Patterns

### Adding a real LLM call

Replace a mock function with a LangChain chain. Example pattern:

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

def generate_outline(premise, genre, context):
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a story architect. Genre: {genre}. Context: {context}"),
        ("human", "Write a JSON outline for: {premise}")
    ])
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"premise": premise, "genre": genre, "context": context})
```

The `llm` variable is module-level; functions can reference it directly (it is `None` when no API key is set — guard against this).

### Adding a new sidebar control

All sidebar widgets are inside the `with st.sidebar:` block. Add new controls there and read their values as plain Python variables (Streamlit returns the widget value immediately).

### Adding a new session state key

Initialize it alongside the existing keys in the `# --- SESSION STATE MANAGEMENT ---` block:

```python
if 'new_key' not in st.session_state:
    st.session_state['new_key'] = <default_value>
```

### Triggering a rerender

Call `st.rerun()` after writing to `st.session_state` inside a button callback to force Streamlit to re-render with updated state.

---

## Genre and Tone Options

Current sidebar options (defined in `app.py`):

- **Genres:** `Techno-Thriller`, `Cyberpunk`, `High Fantasy`, `Romance`
- **Tone Intensity:** `Light`, `Balanced`, `Gritty`, `Dark` (select slider)
- **Author Style:** free-text input, default `"Hemingway-esque brevity"`

---

## Known Limitations / TODOs

- All three generation functions (`generate_outline`, `write_draft`, `critique_draft`) are mocked and must be replaced with real LLM chains before the app produces meaningful output.
- The `llm` object is initialized but never passed to the mock functions; real implementations must use it (and guard for `llm is None`).
- The story bible is only partially updated — only `summary` is appended; `characters` dict is never populated.
- No error handling for invalid API keys, network failures, or malformed LLM responses.
- No tests exist for any logic.
- `python-dotenv` is listed as a dependency but `load_dotenv()` is never called — remove or add the call if `.env` support is desired.

---

## Git Workflow

- Default branches: `main`, `master`
- Feature/AI work branches follow the pattern: `claude/<task-id>`
- No pull request templates or branch protection rules are configured
- Commit messages use short imperative style (e.g., `Create app.py`)

---

## Author

jdiaz — jayremie.diaz@gmail.com
MIT License
