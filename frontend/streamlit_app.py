import sys
from pathlib import Path
from datetime import datetime

import streamlit as st


# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from llm.gemini_client import generate_response


st.set_page_config(
    page_title="E-commerce MCP Multi-Agent Assistant",
    page_icon="🛒",
    layout="wide",
)


PROJECT_MODES = [
    "Auto Mode",
    "Sales Analytics",
    "Internal Reports",
    "Web Intelligence",
    "Recommendation Engine",
]

EXAMPLE_QUESTIONS = [
    "Koje kategorije proizvoda imaju najveći prihod?",
    "Koji regioni imaju najveće kašnjenje dostave?",
    "Koje proizvode treba promovisati?",
    "Da li interni izveštaji potvrđuju pad zadovoljstva kupaca?",
]

MOCK_TOOLS_BY_MODE = {
    "Auto Mode": ["SQL Tool", "Document RAG Tool", "Web Tool"],
    "Sales Analytics": ["SQL Tool"],
    "Internal Reports": ["Document RAG Tool"],
    "Web Intelligence": ["Web Tool"],
    "Recommendation Engine": ["SQL Tool", "Document RAG Tool", "Web Tool"],
}


def initialize_session_state() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "selected_mode" not in st.session_state:
        st.session_state.selected_mode = "Auto Mode"

    if "pending_question" not in st.session_state:
        st.session_state.pending_question = None


def get_routing_result(question: str, selected_mode: str) -> dict:
    """
    Temporary routing logic.

    Later this will be replaced with a real orchestrator agent.
    """

    planned_tools = MOCK_TOOLS_BY_MODE.get(
        selected_mode,
        ["SQL Tool", "Document RAG Tool", "Web Tool"],
    )

    return {
        "selected_mode": selected_mode,
        "planned_tools": planned_tools,
        "reasoning_summary": (
            "Trenutno se koristi ručno izabrani režim iz sidebar-a. "
            "Kasnije će orchestrator agent automatski birati potrebne MCP alate."
        ),
    }


def process_user_message(user_question: str, selected_mode: str) -> None:
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_question,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
        }
    )

    routing_result = get_routing_result(user_question, selected_mode)

    answer = generate_response(
        user_question=user_question,
        routing_result=routing_result,
        chat_history=st.session_state.messages,
    )

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
            "tools": routing_result["planned_tools"],
            "mode": routing_result["selected_mode"],
            "reasoning_summary": routing_result["reasoning_summary"],
            "timestamp": datetime.now().strftime("%H:%M:%S"),
        }
    )


def render_sidebar() -> str:
    st.sidebar.title("🛒 MCP Assistant")

    st.sidebar.markdown(
        """
        Frontend prototip za master rad:  
        **MCP multi-agentski sistem za e-commerce analitiku i objašnjive poslovne preporuke**.
        """
    )

    st.sidebar.markdown("---")

    selected_mode = st.sidebar.radio(
        "Izaberi režim rada:",
        PROJECT_MODES,
        index=PROJECT_MODES.index(st.session_state.selected_mode),
    )

    st.session_state.selected_mode = selected_mode

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Moduli sistema")

    st.sidebar.markdown("- **Sales Analytics** — SQL analiza prodajnih podataka")
    st.sidebar.markdown("- **Internal Reports** — RAG nad PDF/Word izveštajima")
    st.sidebar.markdown("- **Web Intelligence** — spoljašnji tržišni kontekst")
    st.sidebar.markdown("- **Recommendation Engine** — finalne poslovne preporuke")
    st.sidebar.markdown("- **Auto Mode** — sistem sam bira potrebne alate")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Primeri pitanja")

    for question in EXAMPLE_QUESTIONS:
        if st.sidebar.button(question, use_container_width=True):
            st.session_state.pending_question = question

    st.sidebar.markdown("---")

    if st.sidebar.button("🧹 Obriši razgovor", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pending_question = None
        st.rerun()

    return selected_mode


def render_header() -> None:
    st.title("E-commerce MCP Multi-Agent Assistant")

    st.markdown(
        """
        Ova verzija testira povezivanje Streamlit frontend-a sa Gemini LLM API-jem.  
        SQL, RAG, Web i MCP alati su za sada predstavljeni kao planirani/mock izvori.
        """
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.info("📊 SQL Sales Analytics")

    with col2:
        st.info("📄 Internal Reports RAG")

    with col3:
        st.info("🌐 Web Intelligence")

    st.markdown("---")


def render_chat_history() -> None:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            if message["role"] == "assistant":
                selected_mode = message.get("mode", "Auto Mode")
                tools = message.get("tools", [])
                reasoning_summary = message.get("reasoning_summary", "")

                with st.expander("Used sources/tools"):
                    st.markdown(f"**Selected mode:** {selected_mode}")

                    if reasoning_summary:
                        st.markdown(f"**Routing summary:** {reasoning_summary}")

                    if tools:
                        st.markdown("**Planned tools:**")
                        for tool in tools:
                            st.markdown(f"- {tool}")
                    else:
                        st.markdown("No tools selected.")

                timestamp = message.get("timestamp")
                if timestamp:
                    st.caption(f"Generated at {timestamp}")


def render_input_area(selected_mode: str) -> None:
    pending_question = st.session_state.get("pending_question")

    if pending_question:
        process_user_message(
            user_question=pending_question,
            selected_mode=selected_mode,
        )
        st.session_state.pending_question = None
        st.rerun()

    user_question = st.chat_input("Postavi pitanje o e-commerce poslovanju...")

    if user_question:
        process_user_message(
            user_question=user_question,
            selected_mode=selected_mode,
        )
        st.rerun()


def main() -> None:
    initialize_session_state()

    selected_mode = render_sidebar()

    render_header()
    render_chat_history()
    render_input_area(selected_mode)


if __name__ == "__main__":
    main()