from pathlib import Path
from typing import Literal

import streamlit as st

from src.agent.agent import ReActAgent
from src.chatbot import ChatbotBaseline
from src.core.provider_factory import create_provider_from_env
from src.telemetry.metrics import tracker
from src.tools.travel_tools import get_travel_tools


st.set_page_config(page_title="Travel Concierge Chat", page_icon="Chat", layout="wide")

DEFAULT_PROMPTS = [
    "Chi phi tham quan Phu Quoc tron goi, lap ke hoach 3 ngay cho 3 nguoi, ngan sach 10 trieu, uu tien cac diem du lich bien.",
    "Tra loi ngan: VinWonders Phu Quoc phu hop gia dinh co tre em khong?",
    "Giai thich ngan gon ReAct Agent khac chatbot binh thuong o diem nao?",
]


def init_state() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "Xin chao. Ban co the chat tu nhien. Neu cau hoi can lap lich "
                    "trinh Vin/Vinpearl/VinWonders, ReAct Agent se dung tool. "
                    "Cau hoi ngoai mien du lich Vin se duoc chuyen huong lai dung pham vi."
                ),
            }
        ]
    if "last_trace" not in st.session_state:
        st.session_state.last_trace = None
    if "request_metrics" not in st.session_state:
        st.session_state.request_metrics = []


def build_answer(
    query: str,
    mode: Literal["Chatbot", "ReAct Agent"],
    model: str,
    max_steps: int,
) -> tuple[str, list[dict], list[dict]]:
    start_metric_index = tracker.snapshot()
    provider = create_provider_from_env(provider="openai", model=model)
    if mode == "Chatbot":
        runner = ChatbotBaseline(provider)
        answer = runner.run(query)
    else:
        runner = ReActAgent(provider, get_travel_tools(), max_steps=max_steps)
        answer = runner.run(query)
    return answer, tracker.since(start_metric_index), getattr(runner, "trace", [])


def render_sidebar() -> tuple[str, str, int]:
    st.sidebar.title("Lab 3 Chat")
    mode = st.sidebar.radio("Mode", ["ReAct Agent", "Chatbot"], horizontal=True)
    model = st.sidebar.selectbox(
        "Model",
        ["xmtp/mimo-v2.5", "xmtp/mimo-v2.5-pro"],
        index=0,
    )
    max_steps = st.sidebar.slider("Max ReAct steps", min_value=1, max_value=8, value=5)

    st.sidebar.divider()
    st.sidebar.caption("Gateway")
    st.sidebar.code("http://localhost:20128/v1")
    st.sidebar.caption("Logs")
    st.sidebar.code("logs/YYYY-MM-DD.log")

    if st.sidebar.button("Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.last_trace = None
        st.session_state.request_metrics = []
        st.rerun()

    st.sidebar.divider()
    st.sidebar.caption("Quick prompts")
    for idx, prompt in enumerate(DEFAULT_PROMPTS, start=1):
        if st.sidebar.button(f"Prompt {idx}", use_container_width=True):
            st.session_state.pending_prompt = prompt
            st.rerun()

    return mode, model, max_steps


def render_header(mode: str, model: str) -> None:
    st.title("Chatbot vs ReAct Agent")
    st.caption(f"Mode: {mode} | Model: {model} | Backend: Python direct call")


def render_messages() -> None:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("metrics") or message.get("trace"):
                render_message_trace(message.get("metrics", []), message.get("trace", []))

    if st.session_state.last_trace:
        with st.expander("Latest trace"):
            st.code(st.session_state.last_trace)


def render_message_trace(metrics: list[dict], trace: list[dict]) -> None:
    with st.expander("Execution trace", expanded=False):
        if metrics:
            total_cost = sum(metric["cost_estimate"] for metric in metrics)
            total_tokens = sum(metric["total_tokens"] for metric in metrics)
            total_latency = sum(metric["latency_ms"] for metric in metrics)
            st.caption(
                f"LLM calls: {len(metrics)} | Tokens: {total_tokens} | "
                f"Latency: {total_latency} ms | Cost estimate: ${total_cost:.6f}"
            )
            st.dataframe(metrics, use_container_width=True)
        else:
            st.caption("No LLM call for this response.")

        tool_calls = [item for item in trace if item.get("type") == "tool_call"]
        llm_calls = [item for item in trace if item.get("type") == "llm_call"]

        if tool_calls:
            st.caption("Tool calls")
            st.dataframe(tool_calls, use_container_width=True)
        else:
            st.caption("Tool calls: none")

        if llm_calls:
            st.caption("LLM trace")
            st.dataframe(llm_calls, use_container_width=True)


def render_metrics_panel() -> None:
    summary = tracker.summary()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("LLM calls", summary["requests"])
    col2.metric("Total tokens", summary["total_tokens"])
    col3.metric("Est. cost", f"${summary['total_cost_usd']:.6f}")
    col4.metric("Avg latency", f"{summary['avg_latency_ms']} ms")

    if st.session_state.request_metrics:
        with st.expander("Request cost/token log", expanded=True):
            st.dataframe(st.session_state.request_metrics, use_container_width=True)

    log_path = latest_log_path()
    if log_path and log_path.exists():
        with st.expander("Raw JSON log tail"):
            st.code("\n".join(log_path.read_text(encoding="utf-8", errors="ignore").splitlines()[-20:]))


def latest_log_path() -> Path | None:
    logs_dir = Path("logs")
    if not logs_dir.exists():
        return None
    log_files = sorted(logs_dir.glob("*.log"), key=lambda path: path.stat().st_mtime, reverse=True)
    return log_files[0] if log_files else None


def get_prompt() -> str | None:
    pending = st.session_state.pop("pending_prompt", None)
    if pending:
        return pending
    return st.chat_input("Nhap cau hoi...")


def main() -> None:
    init_state()
    mode, model, max_steps = render_sidebar()
    render_header(mode, model)
    render_metrics_panel()
    render_messages()

    prompt = get_prompt()
    if not prompt:
        return

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Dang goi model va xu ly..."):
            try:
                answer, new_metrics, execution_trace = build_answer(prompt, mode, model, max_steps)
                st.session_state.request_metrics.extend(new_metrics)
            except Exception as exc:
                answer = f"Backend error: {type(exc).__name__}: {exc}"
                new_metrics = []
                execution_trace = []
            st.markdown(answer)
            if new_metrics:
                latest_cost = sum(metric["cost_estimate"] for metric in new_metrics)
                latest_tokens = sum(metric["total_tokens"] for metric in new_metrics)
                latest_latency = sum(metric["latency_ms"] for metric in new_metrics)
                st.caption(
                    f"Cost estimate: ${latest_cost:.6f} | "
                    f"Tokens: {latest_tokens} | Latency: {latest_latency} ms | "
                    f"LLM calls: {len(new_metrics)}"
                )
            render_message_trace(new_metrics, execution_trace)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
            "metrics": new_metrics,
            "trace": execution_trace,
        }
    )
    st.session_state.last_trace = (
        f"mode={mode}\nmodel={model}\nmax_steps={max_steps}\n"
        f"new_llm_calls={len(new_metrics)}\n"
        f"tool_calls={len([item for item in execution_trace if item.get('type') == 'tool_call'])}\n"
        f"log_file={Path('logs').resolve()}\\YYYY-MM-DD.log"
    )


if __name__ == "__main__":
    main()
