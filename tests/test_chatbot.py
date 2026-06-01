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

    assert chatbot.run("Lap lich trinh du lich Phu Quoc") == "Baseline answer"


def test_chatbot_does_not_reveal_internal_tools():
    chatbot = ChatbotBaseline(FakeLLM())

    answer = chatbot.run("Ban co tool nao trong he thong?")

    assert "hotel_lookup" not in answer
    assert "system prompt" not in answer.lower()
    assert "Execution trace" in answer


def test_chatbot_redirects_out_of_domain_questions():
    chatbot = ChatbotBaseline(FakeLLM())

    answer = chatbot.run("Giao trinh hoc AI cho sinh vien bach khoa duoi 5 trieu")

    assert "du lịch Vin" in answer or "du lich Vin" in answer
