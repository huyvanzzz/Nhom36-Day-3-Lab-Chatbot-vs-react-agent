# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Trần Quốc Khánh
- **Student ID**: 2A202600679
- **Team Name**: vinAI
- **Date**: 2026-06-01

---

## I. Technical Contribution (15 Points)

My main role in this lab was **Agent Core and integration**. I focused on making the ReAct agent run reliably end-to-end, connecting it with the LLM provider, UI demo, telemetry, and final validation flow.

- **Modules Implemented / Integrated**:
  - `src/agent/agent.py`: ReAct loop, action parser, final answer extraction, max-step control, fallback routing, domain guard, internal-tool guard.
  - `src/chatbot.py`: baseline chatbot for comparison against the ReAct agent.
  - `src/demo.py`: CLI runner for chatbot, agent, and comparison modes.
  - `src/web_server.py`: lightweight Python backend for the HTML chat interface.
  - `chat.html`: simple browser chat UI connected to the backend.
  - `streamlit_app.py`: complete Streamlit chat demo with mode selection, model selection, chat UI, metrics, execution trace, and log display.
  - `src/core/provider_factory.py`: provider creation from `.env`, including the OpenAI-compatible gateway at `http://localhost:20128/v1`.
  - `tests/test_agent.py`, `tests/test_chatbot.py`, `tests/test_provider_factory.py`: validation for parser, final answer detection, guardrails, provider config, and fallback behavior.

- **Code Highlights**:
  - Implemented a controlled ReAct loop:
    - calls the LLM,
    - parses `Action: tool_name({...})`,
    - executes the selected tool,
    - appends `Observation`,
    - stops when `Final Answer:` is produced.
  - Added `max_steps` to prevent infinite loops and unexpected cost growth.
  - Added fallback logic for malformed or empty LLM outputs so the agent can still call the correct travel tools.
  - Added guardrails so the assistant stays focused on Vin/Vinpearl/VinWonders travel and does not expose tool inventory or system prompt details in the final user-facing answer.
  - Integrated telemetry so each run can show LLM call count, latency, token usage, estimated cost, tool calls, and agent trace.

- **Documentation / Integration Explanation**:
  - The ReAct agent is the central integration point. It receives the user query from CLI, HTML backend, or Streamlit UI. It then calls the configured LLM provider, decides whether a tool is needed, executes tools from `src/tools/travel_tools.py`, and returns a final Vietnamese travel answer.
  - The Streamlit UI was built to make the lab easier to present to the instructor: the user can chat normally, while the execution trace below the response shows what happened internally without exposing hidden prompts in the chat answer itself.
  - Final validation result: `pytest -q` passed with **17/17 tests**.

---

## II. Debugging Case Study (10 Points)

- **Problem Description**:
  - During testing, the agent sometimes behaved too freely like a normal chatbot. For example, when the user asked: "Giáo trình học AI cho sinh viên bách khoa dưới 5 triệu", the system could answer the education question even though the project domain is Vin/Vinpearl/VinWonders travel.
  - Another issue appeared when the user asked: "Bạn đã dùng tool gì để lên kế hoạch trên?". A direct answer could reveal internal tool names or implementation details, which is not ideal for a clean chatbot interface.

- **Log Source**:
  - Logs in `logs/2026-06-01.log` showed these events:
    - `AGENT_OUT_OF_DOMAIN`
    - `CHATBOT_OUT_OF_DOMAIN`
    - `AGENT_INTERNAL_QUESTION`
    - `CHATBOT_INTERNAL_QUESTION`
    - `AGENT_PARSE_FALLBACK`
  - Group telemetry summary also recorded:
    - 111 agent end events,
    - 111 tool calls,
    - average agent loop count around 1.77,
    - 28 parser fallback events.

- **Diagnosis**:
  - The root cause was that a general LLM is optimized to be helpful on many topics, so prompt-only control is not enough.
  - For tool questions, the chat answer and the debug trace were mixed conceptually. The user-facing answer should remain natural and safe, while implementation details should be shown separately in the trace panel.
  - For malformed ReAct outputs, the model sometimes returned blank text or more than one action in one step. This made strict parsing unreliable.

- **Solution**:
  - Added a domain guard before the LLM call. Non-travel questions are redirected to Vin/Vinpearl/VinWonders travel planning.
  - Added an internal-tool guard. If the user asks about tools, schema, system prompt, or hidden instructions, the assistant does not reveal them in the chat answer. The UI shows execution details in the trace panel instead.
  - Added deterministic fallback routing in the agent. If parsing fails, the code extracts destination, days, people, budget, and preferences from the query and selects the next safe tool.
  - Added tests to lock these fixes:
    - out-of-domain question should not return unrelated education content,
    - internal tool question should not expose `hotel_lookup` or system prompt,
    - unknown tool returns structured error,
    - max-step fallback still returns a usable answer.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

1. **Reasoning**

   The direct chatbot is simple and fast for general answers, but it has no reliable mechanism to ground facts. The ReAct agent is better for multi-step travel planning because it can break the task into tool calls: hotel lookup, ticket estimate, and itinerary planning. The `Thought -> Action -> Observation` structure makes the model act more like a planner instead of only a text generator.

2. **Reliability**

   The agent can perform worse than the chatbot when the model does not follow the required action format. A chatbot can always produce text, but an agent needs parseable actions. This is why parser fallback, max-step control, and final-answer extraction are important. Without these engineering controls, an agent can become slower, more expensive, or stuck in loops.

3. **Observation**

   Observations are the main advantage of the ReAct design. After a tool returns structured data, the next answer can use concrete hotel names, estimated costs, warnings, and source URLs. This reduces hallucination compared to a baseline chatbot. In this lab, observations also made it possible to build a fallback final answer even when the LLM did not produce a perfect final response.

4. **Engineering Lesson**

   A good agent is not only a prompt. The robust parts are the surrounding software: parser, tool contract, telemetry, fallback, tests, UI trace, and guardrails. The LLM gives reasoning ability, but the code makes the behavior measurable and safe enough for demo.

---

## IV. Future Improvements (5 Points)

- **Scalability**:
  - Replace the current mock travel data with official APIs or a RAG pipeline over verified Vinpearl/VinWonders documents.
  - Move the ReAct flow into a graph/state-machine framework such as LangGraph when the number of tools grows.
  - Add persistent conversation/session storage only when there is a clear product requirement for memory.

- **Safety**:
  - Add a stronger supervisor layer to review tool calls before execution.
  - Add stricter input validation for all tool arguments.
  - Keep separating user-facing answers from internal traces so the assistant does not leak implementation details.

- **Performance**:
  - Cache repeated tool results such as ticket prices and hotel options.
  - Track P50/P95/P99 latency separately for LLM calls and tool calls.
  - Add a smaller fast model for routing and reserve the stronger model for final answer generation.

- **Evaluation**:
  - Build a fixed benchmark set with simple FAQ, multi-step itinerary, missing information, unsafe/out-of-domain prompts, and malformed-action cases.
  - Compare chatbot vs agent on success rate, source quality, latency, token cost, and failure type.

---

> [!NOTE]
> This individual report documents the contribution of Trần Quốc Khánh - 2A202600679 for the Agent Core and integration part of Lab 3.
