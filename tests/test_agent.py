from src.agent.agent import ReActAgent
from src.tools.travel_tools import get_travel_tools


class FakeLLM:
    model_name = "fake-model"

    def __init__(self, responses):
        self.responses = list(responses)

    def generate(self, prompt, system_prompt=None):
        content = self.responses.pop(0)
        return {
            "content": content,
            "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
            "latency_ms": 1,
            "provider": "fake",
        }


def test_parse_action_with_json_args():
    agent = ReActAgent(FakeLLM([]), get_travel_tools())

    action = agent._parse_action(
        'Thought: Need hotels.\nAction: hotel_lookup({"destination": "phu_quoc", "nights": 2})'
    )

    assert action == ("hotel_lookup", '{"destination": "phu_quoc", "nights": 2}')


def test_final_answer_terminates_loop():
    agent = ReActAgent(
        FakeLLM(["Final Answer: Lịch trình đã sẵn sàng."]),
        get_travel_tools(),
    )

    assert agent.run("Lap lich trinh Phu Quoc") == "Lịch trình đã sẵn sàng."


def test_unknown_tool_returns_error_observation():
    agent = ReActAgent(FakeLLM([]), get_travel_tools())

    result = agent._execute_tool("missing_tool", "{}")

    assert "UNKNOWN_TOOL" in result


def test_max_steps_returns_fallback():
    agent = ReActAgent(
        FakeLLM(['Thought: Need hotels.\nAction: hotel_lookup({"destination": "phu_quoc"})']),
        get_travel_tools(),
        max_steps=1,
    )

    answer = agent.run("Lap lich trinh Phu Quoc")

    assert "Day la lich trinh goi y" in answer
    assert "Nguon tham khao" in answer


def test_agent_does_not_reveal_internal_tools():
    agent = ReActAgent(FakeLLM([]), get_travel_tools())

    answer = agent.run("Ban da dung tool gi de len ke hoach tren?")

    assert "hotel_lookup" not in answer
    assert "system prompt" not in answer.lower()
    assert "Execution trace" in answer


def test_agent_redirects_out_of_domain_questions():
    agent = ReActAgent(FakeLLM([]), get_travel_tools())

    answer = agent.run("Giao trinh hoc AI cho sinh vien bach khoa duoi 5 trieu")

    assert "du lịch Vin" in answer or "du lich Vin" in answer
    assert "giáo trình" not in answer.lower()