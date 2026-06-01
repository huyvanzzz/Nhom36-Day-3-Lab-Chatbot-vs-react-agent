# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Nguyễn Ngọc Hảo
- **Student ID**: 2A202600903
- **Date**: 2026-06-01

---

## I. Technical Contribution (15 Points)

Trong Lab 3, vai trò chính của tôi là **Report and demo script** cho hệ thống **Vin Travel Concierge Agent**. Tôi phụ trách tổng hợp kết quả nhóm, ánh xạ rubric, ghi lại trace thành công/thất bại và chuẩn bị checklist demo để nhóm có thể trình bày rõ sự khác biệt giữa chatbot baseline và ReAct Agent.

- **Modules / Files Contributed**:
  - `report/group_report/TEMPLATE_GROUP_REPORT.md`: hoàn thiện group report cho toàn bộ dự án.
  - `logs/2026-06-01.log`: dùng làm nguồn evidence cho phần trace, metrics và failure analysis.
  - `README.md`: tham chiếu cách chạy demo CLI, web server và Streamlit UI.
  - `streamlit_app.py`: tham chiếu demo UI, metric panel và execution trace phục vụ phần trình bày.

- **Main Outputs**:
  - Viết phần **Executive Summary** mô tả mục tiêu của project: so sánh chatbot trực tiếp với ReAct Agent trong domain Vin/Vinpearl/VinWonders travel concierge.
  - Hoàn thiện phần **System Architecture & Tooling**, bao gồm flowchart ReAct loop và inventory của 3 tools: `hotel_lookup`, `ticket_offer_lookup`, `itinerary_planner`.
  - Tổng hợp phần **Telemetry & Performance Dashboard** từ JSON logs: số LLM calls, latency, token usage, estimated cost, agent loop count, tool call distribution và status distribution.
  - Viết phần **Root Cause Analysis** cho các lỗi quan trọng: out-of-domain answer, internal tool question, malformed/missing ReAct action và max-step timeout.
  - Hoàn thiện **Rubric Mapping and Self-Assessment** để chứng minh project đạt các tiêu chí chấm điểm: chatbot baseline, agent v1/v2, trace quality, evaluation, flowchart, code quality và bonus.
  - Chuẩn bị nội dung **live demo checklist**: chạy CLI compare, chạy web UI, chạy Streamlit UI, hỏi các prompt demo và mở execution trace/logs để giải thích.

- **Documentation Link to ReAct Loop**:
  - Phần report giải thích cách agent đi qua chu trình `Thought -> Action -> Observation -> Final Answer`.
  - Tôi không trực tiếp implement agent core, nhưng đã đọc trace và code để mô tả đúng cơ chế parser, fallback action, max steps, domain guard và internal-tool guard trong báo cáo.

---

## II. Debugging Case Study (10 Points)

### Problem Description

Một lỗi đáng chú ý trong quá trình đánh giá là model đôi khi trả về output không đúng schema ReAct, ví dụ blank content, direct prose hoặc nhiều `Action` trong cùng một turn. Khi đó parser không thể chắc chắn action nào nên được execute. Nếu không xử lý, agent có thể dừng sớm, trả lời thiếu căn cứ hoặc lặp nhiều bước gây tăng latency/cost.

### Log Source

Nguồn evidence lấy từ `logs/2026-06-01.log`. Một ví dụ trong log:

```text
event: AGENT_PARSE_FALLBACK
data: {"step": 1, "content": "", "tool_name": "hotel_lookup"}
```

Trace khác cũng cho thấy agent gặp trường hợp model sinh nhiều action trong một bước, sau đó hệ thống vẫn ghi nhận `TOOL_CALL` và tiếp tục xử lý thay vì crash.

### Diagnosis

Nguyên nhân chính là model nhỏ/nhanh `xmtp/mimo-v2.5` không phải lúc nào cũng tuân thủ format ReAct nghiêm ngặt. Dù system prompt yêu cầu:

```text
Thought: ...
Action: tool_name({"key": "value"})
```

model vẫn có thể:

- Trả lời trực tiếp mà không có `Final Answer`.
- Trả blank content.
- Sinh nhiều action trong một response.
- Viết prose trước khi tool call làm parser khó xử lý.

Đây là failure thuộc nhóm **parser / schema-following reliability**, không phải lỗi của tool data.

### Solution

Agent v2 bổ sung deterministic fallback routing trong `src/agent/agent.py`. Khi `_parse_action()` không tìm được action hợp lệ và `_extract_final_answer()` cũng không có kết quả, agent dùng `_fallback_action()` để chọn tool an toàn dựa trên đặc điểm query:

- Destination: Phú Quốc hoặc Nha Trang.
- Số ngày / số đêm.
- Số người lớn / trẻ em.
- Ngân sách.
- Preference như beach, family, relax.

Fallback sẽ gọi các tool theo thứ tự hợp lý:

```text
hotel_lookup -> ticket_offer_lookup -> itinerary_planner
```

Nhờ vậy agent vẫn có observation thật từ tool và có thể build fallback final answer nếu model tiếp tục không tuân thủ schema.

### Result

Sau khi có fallback, hệ thống không bị crash khi gặp malformed action. Log có `AGENT_PARSE_FALLBACK`, `TOOL_CALL`, sau đó có thể kết thúc bằng `success`, `fallback_final` hoặc `max_steps` tùy tình huống. Điều này giúp report chứng minh được failure handling và trace quality, đồng thời hỗ trợ phần bonus về guardrails.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

1. **Reasoning**

Chatbot baseline trả lời trực tiếp từ LLM nên phù hợp với câu hỏi đơn giản như FAQ hoặc tư vấn chung. Tuy nhiên, với bài toán nhiều bước như lập lịch trình 3 ngày, tính ngân sách, chọn khách sạn và ước tính vé, chatbot dễ đưa ra câu trả lời nghe hợp lý nhưng thiếu nguồn kiểm chứng.

ReAct Agent tốt hơn ở điểm nó chia bài toán thành các bước rõ ràng. `Thought` giúp model xác định cần làm gì tiếp theo, `Action` gọi tool để lấy dữ liệu có cấu trúc, còn `Observation` đưa kết quả thật quay lại prompt. Vì vậy final answer có căn cứ hơn, có chi phí ước tính, warning mock data và source URL.

2. **Reliability**

Agent không phải lúc nào cũng tốt hơn chatbot. Với câu hỏi rất đơn giản, chatbot có thể trả lời nhanh hơn vì chỉ cần một LLM call và không tốn tool loop. Agent có thể chậm hơn do phải gọi LLM nhiều lần và parse action. Ngoài ra, nếu model không tuân thủ format, agent cần fallback để tránh lỗi parser.

Điểm quan trọng là ReAct Agent phù hợp hơn cho bài toán có hành động, dữ liệu, trace và kiểm soát lỗi. Chatbot phù hợp hơn cho câu hỏi ngắn, ít rủi ro, không cần tool.

3. **Observation**

Observation là phần làm agent khác chatbot rõ nhất. Sau khi tool trả về hotel, ticket hoặc itinerary data, agent không còn phải tự bịa thông tin. Nó có thể dựa vào observation để tổng hợp câu trả lời cuối. Trong report nhóm, các trace cho thấy agent gọi tool, nhận JSON observation, rồi đưa ra câu trả lời có lịch trình, chi phí, warning và nguồn tham khảo.

Tôi nhận ra rằng trong hệ thống agentic, trace quan trọng gần như ngang với final answer. Nếu chỉ nhìn câu trả lời cuối, rất khó biết agent đúng vì lý do gì. Khi có logs và execution trace, nhóm có thể phân tích được lỗi đến từ prompt, parser, tool, provider hay giới hạn max steps.

---

## IV. Future Improvements (5 Points)

- **Scalability**:
  - Thay mock data bằng RAG hoặc API chính thức từ Vinpearl/VinWonders.
  - Lưu session và trace vào database để có thể phân tích nhiều lượt demo, không chỉ đọc file log cục bộ.
  - Chuyển ReAct loop sang LangGraph hoặc state machine để dễ kiểm soát branching, retry và fallback.

- **Safety**:
  - Thêm supervisor layer để kiểm tra final answer trước khi trả về người dùng.
  - Tách rõ user-facing answer và debug trace để tránh lộ system prompt, tool schema hoặc thông tin nội bộ.
  - Mở rộng guardrail cho prompt injection, yêu cầu secrets, câu hỏi ngoài domain và nội dung không an toàn.

- **Performance**:
  - Dùng tool routing deterministic trước khi gọi LLM để giảm số vòng ReAct không cần thiết.
  - Cache kết quả tool cho các query phổ biến như vé VinWonders Phú Quốc hoặc lịch trình Nha Trang 2 ngày.
  - Theo dõi P50/P99 latency, token usage và cost theo từng mode: chatbot, agent v1, agent v2.

- **Evaluation**:
  - Tạo bộ test case cố định cho simple FAQ, multi-step itinerary, missing information, out-of-domain, internal-tool question và malformed action.
  - Tự động sinh bảng so sánh chatbot vs agent từ logs để report ít phụ thuộc vào copy thủ công.

---

## Commit Messages for My Role

Các commit phù hợp với phần việc của tôi:

```text
Nguyen Ngoc Hao - 2A202600903, Group report has done!
Nguyen Ngoc Hao - 2A202600903, Rubric mapping has done!
Nguyen Ngoc Hao - 2A202600903, Successful and failed trace documentation has done!
Nguyen Ngoc Hao - 2A202600903, Live demo checklist has done!
Nguyen Ngoc Hao - 2A202600903, Individual report has done!
```
