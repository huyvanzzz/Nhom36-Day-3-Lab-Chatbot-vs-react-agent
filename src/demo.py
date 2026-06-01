import argparse
import sys

from src.agent.agent import ReActAgent
from src.chatbot import ChatbotBaseline
from src.core.provider_factory import create_provider_from_env
from src.tools.travel_tools import get_travel_tools


DEFAULT_QUERY = (
    "Gia dinh toi co 2 nguoi lon, 2 tre em, muon di Phu Quoc 3 ngay 2 dem "
    "trong thang 7, ngan sach khoang 15 trieu, uu tien nghi duong va cho tre con choi. "
    "Hay lap ke hoach giup toi."
)


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description="Run the Travel Concierge Lab 3 demo.")
    parser.add_argument("--mode", choices=["chatbot", "agent", "compare"], default="agent")
    parser.add_argument("--provider", choices=["openai", "google"], default="openai", help="LLM provider")
    parser.add_argument("--model", help="Model name for the selected provider")
    parser.add_argument("--query", default=DEFAULT_QUERY, help="User query to send to the system")
    parser.add_argument("--max-steps", type=int, default=5, help="Maximum ReAct steps")
    args = parser.parse_args()

    provider = create_provider_from_env(provider=args.provider, model=args.model)

    if args.mode in {"chatbot", "compare"}:
        chatbot = ChatbotBaseline(llm=provider)
        print("\n=== Chatbot Baseline Answer ===\n")
        print(chatbot.run(args.query))

    if args.mode in {"agent", "compare"}:
        agent = ReActAgent(llm=provider, tools=get_travel_tools(), max_steps=args.max_steps)
        print("\n=== ReAct Agent Answer ===\n")
        print(agent.run(args.query))


if __name__ == "__main__":
    main()
