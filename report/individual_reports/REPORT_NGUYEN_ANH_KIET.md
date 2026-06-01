# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Nguyễn Anh Kiệt
- **Student ID**: 2A202600677
- **Date**: 2026-06-01

---

## I. Technical Contribution (15 Points)

*Describe your specific contribution to the codebase (e.g., implemented a specific tool, fixed the parser, etc.).*

- **Modules Implementated**: `code/src/tools/travel_tools.py`, `code/tests/test_tools.py`
- **Code Highlights**: I implemented the travel tool layer for the Vin Travel Concierge domain. The file defines mock data for Phú Quốc and Nha Trang hotels/tickets, plus three callable tools: `hotel_lookup`, `ticket_offer_lookup`, and `itinerary_planner`. Each tool returns structured dictionaries so the ReAct agent can turn tool observations into a final user-facing itinerary.
- **Documentation**: The ReAct agent receives the tools through `get_travel_tools()`. Each tool entry includes a `name`, `description`, `args_schema`, and `func`, which lets the agent build its tool prompt, parse an action such as `hotel_lookup({...})`, execute the matching Python function, and append the returned result as an `Observation`. I also included source URLs and warnings in the tool outputs so the final answer can clearly mark prices and schedules as mock lab data that must be verified on official Vinpearl/VinWonders sources.

---

## II. Debugging Case Study (10 Points)

*Analyze a specific failure event you encountered during the lab using the logging system.*

- **Problem Description**: The agent could produce a travel plan, but early tool outputs were not reliable enough for evaluation because a missing destination, an unsupported destination format, or missing price warning could make the final answer look more certain than the mock data allowed.
- **Log Source**: Group telemetry shows `AGENT_PARSE_FALLBACK` and tool-call recovery events in `logs/2026-06-01.log`. For my tool layer, the related validation evidence is in `code/tests/test_tools.py`, especially checks that hotel and ticket outputs include `source_url`, and itinerary outputs include `estimated_cost_vnd` plus `sources`.
- **Diagnosis**: The issue was mainly in the tool specification and mock-data contract, not only in the LLM. The agent can only reason safely if the tools return predictable fields. Without consistent fields such as `status`, `source_url`, `warnings`, and `estimated_cost_vnd`, the LLM may hallucinate prices or omit source verification.
- **Solution**: I normalized destination input in `_normalize_destination`, added structured `status` values, included official source URLs in hotel/ticket outputs, calculated ticket subtotals from adult and child counts, and added explicit warnings that values are mock data for lab demo. I also added tests to confirm the travel tools return sources and budget/cost data.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

*Reflect on the reasoning capability difference.*

1.  **Reasoning**: The `Thought` block helps the agent break a travel request into smaller decisions: first identify the destination and group size, then look up hotel options, then calculate ticket cost, then build the itinerary. A direct chatbot may answer faster, but it often mixes assumptions and final recommendations without showing which facts came from a tool.
2.  **Reliability**: The agent can perform worse than the chatbot when the LLM does not follow the required ReAct action format, when it tries to call more than one tool at once, or when the tool data does not cover the user's destination. In those cases, the chatbot may give a smoother response, while the agent needs parser fallback and guardrails to avoid failing awkwardly.
3.  **Observation**: Observations make the next step more grounded. For example, after `hotel_lookup` returns hotel options and warnings, the agent can use that information when calling `itinerary_planner` and when writing the final answer. The observation also forces the answer to respect available mock data instead of inventing exact booking details.

---

## IV. Future Improvements (5 Points)

*How would you scale this for a production-level AI agent system?*

- **Scalability**: Replace in-memory mock dictionaries with a verified data service or database for hotels, tickets, packages, and availability. Tool calls should support caching and async execution so the agent can handle many users without blocking.
- **Safety**: Add stricter schema validation with Pydantic or JSON Schema before each tool call, and return a controlled error whenever destination, date, budget, or passenger count is missing or invalid. The final answer should always include source and verification warnings for prices.
- **Performance**: Add RAG over official Vinpearl/VinWonders pages so the agent can retrieve up-to-date policies and promotions. For a larger tool set, add tool retrieval so the prompt only includes relevant tools instead of every available tool.

---

> [!NOTE]
> Submit this report by renaming it to `REPORT_[YOUR_NAME].md` and placing it in this folder.
