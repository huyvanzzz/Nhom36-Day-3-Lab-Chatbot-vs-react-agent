# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Nhan Khánh Đình
- **Student ID**: 2A202600673
- **Date**: 2026-06-01

---

## I. Technical Contribution (15 Points)

My primary responsibility in this project was the **Telemetry and Testing layer**. This system ensures that every interaction with the LLM is monitored for performance, cost, and reliability, while the testing suite guarantees that the Agent's logic remains robust across different models and tools.

- **Modules Implemented**:

  - `src/telemetry/logger.py`
  - `src/telemetry/metrics.py`
  - `tests/test_agent.py`
  - `tests/test_tools.py`

- **Main Contribution 1: Structured JSON Logging System**

  I implemented a centralized logging system in `src/telemetry/logger.py` that simulates industry-standard practices. Instead of simple text logs, this module produces structured JSON events, which are essential for large-scale analysis and automated debugging.

  The `IndustryLogger` class manages two handlers: a console handler for real-time developer feedback and a file handler that saves logs to the `logs/` directory with a date-based filename (e.g., `2026-06-01.log`). This structure allows us to track specific event types like `LLM_METRIC` or `AGENT_STEP` with consistent timestamps and data payloads.

- **Main Contribution 2: Performance and Cost Tracking**

  In `src/telemetry/metrics.py`, I developed the `PerformanceTracker` class to monitor the operational costs of our AI system. Since LLM usage can be expensive, it was critical to implement a way to estimate costs in real-time.

  I defined a pricing dictionary `MODEL_PRICING_USD_PER_1M` to store input and output costs for different models like `xmtp/mimo-v2.5`. The tracker captures the `prompt_tokens`, `completion_tokens`, and `latency_ms` for every request, calculating a cost estimate that is logged immediately. This data is also used to generate a session summary, providing insights into the average latency and total expenditure.

- **Main Contribution 3: Provider-level Telemetry Integration**

  To ensure accurate data collection, I integrated telemetry hooks directly into the provider layer. In `src/core/openai_provider.py` and `src/core/gemini_provider.py`, I added logic to measure the exact time taken for each generation and extract token usage metadata from the provider's response.

  ```python
  start_time = time.time()
  # ... LLM call ...
  end_time = time.time()
  latency_ms = int((end_time - start_time) * 1000)
  ```

  This data is returned in a standardized dictionary format, which the `PerformanceTracker` then consumes to update the global metrics.

- **Main Contribution 4: Automated Testing Suite**

  I established a comprehensive testing framework in the `tests/` directory to validate the core components of the project. This included unit tests for the ReAct Agent's parser, tool execution, and the baseline chatbot's behavior.

  For example, in `tests/test_agent.py`, I created `FakeLLM` classes to simulate different model responses, allowing us to test how the agent handles tool calls, final answers, and unknown tools without spending actual API credits. This ensures that any changes to the core logic do not break existing functionality.

- **Main Contribution 5: Failure Trace Collection**

  I enhanced the error handling capabilities of the logger to support failure trace collection. By using the `exc_info=True` parameter in the `logger.error` method, the system automatically captures the full Python stack trace whenever an exception occurs.

  ```python
  def error(self, msg: str, exc_info=True):
      self.logger.error(msg, exc_info=exc_info)
  ```

  This is vital for debugging complex issues in the ReAct loop, such as malformed JSON responses from the LLM or unexpected tool failures, as it provides the exact line number and call history leading to the error.

---

## II. Debugging Case Study (10 Points)

- **Problem Description**

  A recurring issue during the development of the ReAct Agent was the "Parser Failure" event. The agent would occasionally crash or stop responding when the LLM provided a response that didn't strictly follow the `Action: tool_name({"arg": "val"})` format. Specifically, the model would sometimes wrap the JSON arguments in extra text or markdown code blocks, which the initial parser could not handle.

- **Log Source**

  I identified this issue by reviewing the JSON logs in `logs/2026-06-01.log`. The logs showed multiple `ERROR` events where the `data` field contained a `JSONDecodeError`. By looking at the preceding `AGENT_STEP` event, I could see the raw content returned by the LLM:

  ```json
  {
    "event": "AGENT_STEP",
    "data": {
      "content": "Thought: I need to look up a hotel.\nAction: hotel_lookup({\"destination\": \"phu_quoc\"}) ... here are some options."
    }
  }
  ```

- **Diagnosis**

  The diagnosis revealed that the LLM was "leaking" conversational text into the Action block. Because the `ReActAgent` used a simple string split or an inflexible regex, it attempted to pass the entire string (including the trailing "here are some options") to `json.loads()`, which naturally failed. This highlighted a vulnerability in how the agent interpreted the model's instructions.

- **Solution**

  To solve this, I refined the regular expression in `src/agent/agent.py` to specifically target the JSON portion of the Action line. I also added a robust try-except block around the parser and implemented a unit test `test_parse_action_with_json_args` in `tests/test_agent.py` that specifically tests for trailing text and malformed JSON. This ensures the agent can now gracefully handle "noisy" outputs from the model.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

1. **Reasoning**

   The introduction of the `Thought` block in the ReAct Agent provides a critical layer of deliberation that the baseline Chatbot lacks. While the Chatbot answers directly based on its training data, the Agent uses the `Thought` space to decompose a user's request into smaller, actionable steps. This leads to much more accurate results for complex queries like "Plan a 3-day trip to Phu Quoc with a 15M VND budget," where multiple tools must be coordinated.

2. **Reliability**

   However, this increased power comes with higher sensitivity. The ReAct Agent is significantly more prone to failure if the model's output format deviates even slightly. In my testing, the Chatbot was more "reliable" in terms of always providing _some_ answer, even if it was a hallucination. The Agent, conversely, is only as reliable as its parser and the tool's error handling. This reinforces the need for the strict telemetry and testing systems I implemented.

3. **Observation**

   The `Observation` step is what truly grounds the Agent in reality. By receiving actual data from tools (like real hotel names and prices), the Agent can correct its internal assumptions. I observed that the Agent would often change its "Thought" in the next step after seeing a tool result—for example, if a hotel was too expensive, the next Thought would focus on finding a cheaper alternative. This dynamic feedback loop is absent in the baseline Chatbot.

---

## IV. Future Improvements (5 Points)

- **Scalability**

  To handle higher traffic, I would implement an asynchronous logging queue (using a library like `structlog` or a message broker). This would ensure that writing logs to disk or sending metrics to a dashboard does not block the LLM's response time, keeping the user experience smooth.

- **Traceability**

  Finally, I would like to build a web-based dashboard that parses the JSON logs created by my telemetry system. This would allow developers to visualize the Agent's "Thought" process and cost metrics in real-time, making it much easier to identify bottlenecks and optimize the ReAct loop.

---
