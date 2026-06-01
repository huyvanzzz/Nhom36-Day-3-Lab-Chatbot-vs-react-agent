from src.chatbot import ChatbotBaseline


class FakeLLM:
    model_name = "fake-model"

    def generate(self, prompt, system_prompt=None):
        return {
            "content": "Baseline answer",
            "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
            "latency_ms": 1,
            "provider": "fake",
        }


def test_chatbot_baseline_returns_direct_llm_answer():
    chatbot = ChatbotBaseline(FakeLLM())

    assert chatbot.run("Question") == "Baseline answer"