# Individual Report: Lab 3 - Chatbot vs ReAct Agent
- **Student Name**: Nguyen Van Huy
- **Student ID**: 2A202600773
- **Date**: 2026-06-01

---

## I. Technical Contribution (15 Points)

My main responsibility in this project was the **Provider/config layer**. This part connects the chatbot, ReAct agent, CLI demo, and UI to the selected LLM provider through one shared configuration flow. I also supported the team by merging GitHub branches and checking that the integrated code still used the correct provider configuration.

- **Modules Implemented**:
  - `src/core/provider_factory.py`
  - `src/core/openai_provider.py`
  - `src/core/local_provider.py`
  - `.env.example`

- **Main Contribution 1: Provider factory from environment config**

  I implemented the provider factory so the rest of the system does not need to hardcode API keys, model names, or gateway URLs. The chatbot and ReAct agent can call:

  ```python
  provider = create_provider_from_env(provider="openai", model=model)
  ```

  and the provider layer handles the actual configuration.

  In `src/core/provider_factory.py`, I added logic to:

  - read provider config from environment variables and `.env`
  - support `openai` and `google/gemini` provider names
  - select a model from explicit arguments or default config
  - pass the correct API key and base URL into the provider class
  - raise a clear error when an unsupported provider is requested

- **Main Contribution 2: OpenAI-compatible gateway setup**

  The lab used an OpenAI-compatible local gateway instead of the normal OpenAI endpoint. I configured the provider layer to support:

  ```txt
  http://localhost:20128/v1
  ```

  This was important because the OpenAI Python client can still be used, but only if the `base_url` is passed correctly. In `src/core/openai_provider.py`, the provider accepts `base_url` and initializes:

  ```python
  self.client = OpenAI(api_key=self.api_key, base_url=base_url)
  ```

  This allows the same `OpenAIProvider` class to work with the lab gateway while keeping the rest of the code unchanged.

- **Main Contribution 3: `.env` parsing for lab-specific config**

  The project needed to support both normal `.env` style and the looser lab format. I added parsing for both:

  ```txt
  OPENAI_API_KEY=...
  OPENAI_BASE_URL=...
  DEFAULT_MODEL=...
  ```

  and:

  ```txt
  host: http://localhost:20128/v1
  api_key1: ...
  api_key2: ...
  model: xmtp/mimo-v2.5, xmtp/mimo-v2.5-pro
  ```

  This made the project easier to run during the lab because different members could use the provided lab config format without changing source code.

- **Main Contribution 4: Model selection**

  I configured the project to use the lab models:

  ```txt
  xmtp/mimo-v2.5
  xmtp/mimo-v2.5-pro
  ```

  When the config contains multiple models separated by a comma, the provider factory selects the first model as the default. This is handled by `_first_model(...)` in `src/core/provider_factory.py`.

  Example:

  ```python
  _first_model("xmtp/mimo-v2.5, xmtp/mimo-v2.5-pro")
  ```

  returns:

  ```txt
  xmtp/mimo-v2.5
  ```

- **Main Contribution 5: GitHub branch merging and integration**

  Besides the provider/config code, I also helped merge the team's GitHub branches into the working project branch. This task was important because each member worked on a different part:

  - agent core and integration
  - travel tools and mock data
  - provider/config layer
  - telemetry and tests
  - report and demo materials

  During merging, I checked that my provider/config changes did not overwrite other members' work. I also made sure the integrated project still used the shared provider factory, so the agent, chatbot, and demo could all call the same LLM configuration instead of creating separate provider setups.

- **Documentation**

  My provider/config layer interacts with the ReAct loop indirectly. The ReAct agent does not call the gateway by itself. Instead, it receives an `LLMProvider` instance from the provider factory. This separation keeps the ReAct logic focused on `Thought -> Action -> Observation -> Final Answer`, while my provider layer handles model connection, API key loading, gateway URL normalization, and model selection.

---

## II. Debugging Case Study (10 Points)

- **Problem Description**

  During integration, one issue was that the model configuration could fail or behave inconsistently when different config formats were used. Some settings followed normal `.env` syntax such as `OPENAI_BASE_URL=...`, while the lab gateway notes could also use a loose format such as `host: ...`, `api_key1: ...`, and `model: ...`.

  If the provider layer only supported one format, the chatbot or ReAct agent might not connect to the intended OpenAI-compatible gateway. This would break the full system even if the agent loop and tools were implemented correctly.

- **Log Source**

  The logging system writes events to:

  ```txt
  logs/YYYY-MM-DD.log
  ```

  The relevant events for this type of issue are the LLM call events, for example:

  ```txt
  event: LLM_METRIC
  data: provider, model, prompt_tokens, completion_tokens, total_tokens, latency_ms
  ```

  and agent step events:

  ```txt
  event: AGENT_STEP
  data: step, model, provider, latency_ms, content
  ```

  These logs help confirm whether the system is actually calling the expected provider/model after config changes.

- **Diagnosis**

  The root cause was not the ReAct prompt or the travel tools. The issue was at the provider/config boundary. The project needed a single config loader that could understand the lab's gateway settings and convert them into the parameters expected by the OpenAI-compatible client.

  The risky cases were:

  - missing `OPENAI_BASE_URL`
  - base URL written as `host: http://localhost:20128/v1`
  - multiple models written in one line, such as `xmtp/mimo-v2.5, xmtp/mimo-v2.5-pro`
  - API key stored under `api_key1` or `api_key2` instead of only `OPENAI_API_KEY`

  Without handling these cases, the system could silently use the wrong model, fail to connect to the gateway, or require manual code changes on each machine.

- **Solution**

  I implemented `src/core/provider_factory.py` to centralize this logic. The fix included:

  - loading environment variables first
  - reading `.env` only as config input
  - supporting both `KEY=value` and `key: value`
  - mapping `host` to the OpenAI-compatible `base_url`
  - selecting from `OPENAI_API_KEY`, `api_key`, `api_key1`, or `api_key2`
  - normalizing the gateway URL to `http://localhost:20128/v1`
  - selecting the first model if multiple models are provided

  After this change, the ReAct agent and chatbot could be initialized through the same provider factory, which reduced duplicated setup and made the merged project more stable.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

1. **Reasoning**

   The `Thought` block helps the agent decide whether it needs to call a tool before answering. A direct chatbot usually answers immediately from the model's internal knowledge, which can be fast but may hallucinate prices, tickets, or itinerary details. In this project, the ReAct agent can first reason that it needs hotel data, ticket data, or itinerary data, then call the matching tool before writing the final answer.

   From my provider/config perspective, this also made model reliability more important. If the provider config points to the wrong model or gateway, the ReAct loop can fail even when the agent code is correct. That is why a stable provider factory is necessary for the ReAct design to work consistently.

2. **Reliability**

   The agent can perform worse than the chatbot when the model does not follow the required action format. For example, instead of returning one clean action like:

   ```txt
   Action: hotel_lookup({"destination": "phu_quoc"})
   ```

   the model may return long prose, multiple actions, or malformed JSON. In those cases, the ReAct agent needs parser handling, fallback logic, and max-step limits. A direct chatbot may look smoother because it can always produce text, but that answer may not be grounded in tool data.

   This showed me that ReAct is more powerful, but also more sensitive to model behavior, prompt format, and provider stability.

3. **Observation**

   Observations are the main difference between guessing and using external information. After a tool call, the agent receives structured data such as hotel options, ticket estimates, itinerary items, warnings, and source URLs. The next step can then use that observation to refine the answer.

   For example, after a hotel lookup, the agent can use the hotel price and area in the next step. After a ticket lookup, it can include a more realistic cost estimate. This makes the final answer more useful than a direct chatbot response, especially for travel planning where users expect concrete budgets and warnings.

---

## IV. Future Improvements (5 Points)

- **Scalability**

  I would improve the provider layer so it can support more providers and fallback strategies. For example, the system could try the primary model first, then automatically switch to a backup model if the gateway times out or returns an error. This would make the ReAct agent more reliable during demos and production usage.

- **Safety**

  I would add stricter validation for provider config. The system should check that required values such as API key, base URL, and model name are present before the agent starts running. It should also make sure secrets are never printed in logs, traces, UI panels, or error messages.

- **Performance**

  I would add timeout and retry settings to the provider layer. ReAct agents often make multiple LLM calls, so one slow provider call can make the whole conversation slow. A production version should track provider latency, retry temporary failures, and allow switching between `xmtp/mimo-v2.5` and `xmtp/mimo-v2.5-pro` depending on speed and answer quality.

- **Team Integration**

  For GitHub collaboration, I would improve the merge process by requiring each branch to pass a small checklist before merging:

  - no `.env` file committed
  - no logs or cache files committed
  - provider config still points to the lab gateway
  - tests or demo commands still run after merge
  - files are grouped by each member's responsibility

  This would reduce merge conflicts and make the final submission cleaner.

---
