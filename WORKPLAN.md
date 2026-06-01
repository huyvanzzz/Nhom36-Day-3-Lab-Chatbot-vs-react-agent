# Kế Hoạch Thực Hiện Lab 3: Chatbot vs ReAct Agent

Tài liệu này tổng hợp các yêu cầu từ `README.md`, `INSTRUCTOR_GUIDE.md`, `EVALUATION.md`, và `SCORING.md`, rồi chuyển thành danh sách việc cần làm kèm file đích cụ thể.

## 1. Mục Tiêu Cần Đạt

- Có một chatbot baseline tối giản để so sánh với agent.
- Hoàn thiện ReAct loop trong `src/agent/agent.py`.
- Hỗ trợ đổi provider giữa OpenAI, Gemini, và Local qua interface `LLMProvider`.
- Ghi log có cấu trúc để phân tích lỗi, latency, token, và số bước.
- Có bộ test đủ để kiểm tra provider local và hành vi agent.
- Chuẩn bị report nhóm và report cá nhân theo template có sẵn.

## 2. Những File Cần Làm Việc

| File / Thư Mục | Việc cần làm | Ghi chú |
| :--- | :--- | :--- |
| `src/agent/agent.py` | Implement ReAct loop đầy đủ: tạo system prompt, gọi LLM, parse `Thought/Action/Observation`, thực thi tool, lặp tới `Final Answer`, chặn vòng lặp vô hạn bằng `max_steps`. | Đây là file trọng tâm của lab. |
| `src/core/llm_provider.py` | Giữ interface chuẩn cho các provider và đảm bảo output thống nhất cho `generate()` và `stream()`. | Không nên phá vỡ format trả về hiện có. |
| `src/core/openai_provider.py` | Kiểm tra cách gọi API, format message, và shape dữ liệu trả về. | Dùng để đổi provider mượt mà. |
| `src/core/gemini_provider.py` | Kiểm tra cách truyền system prompt và shape dữ liệu trả về. | Cần tương thích với agent. |
| `src/core/local_provider.py` | Xác nhận local model chạy được, prompt format ổn, và output trả về có đủ `usage` + `latency_ms`. | Cần cho chế độ CPU / offline. |
| `src/telemetry/logger.py` | Bảo đảm log JSON nhất quán cho các event như start, step, tool call, observation, end, error. | Dùng để phục vụ phần đánh giá và debug. |
| `src/tools/` (tạo mới nếu chưa có) | Định nghĩa các tool mà agent sẽ gọi. | README đã nói đây là extension point cho tool custom. |
| `chatbot.py` hoặc file tương đương ở root | Tạo baseline chatbot tối giản để chạy đối chứng với agent. | `INSTRUCTOR_GUIDE.md` có nhắc chạy `chatbot.py`; repo hiện chưa thấy file này. |
| `tests/` | Thêm test cho provider local và các case chính của agent. | Ít nhất nên có test cho parse, tool call, và dừng đúng bước. |
| `report/group_report/` | Điền và đổi tên report nhóm theo template. | Dựa trên kết quả thực nghiệm cuối cùng. |
| `report/individual_reports/` | Điền và đổi tên report cá nhân theo template. | Mỗi người cần nộp riêng. |

## 3. Thứ Tự Thực Hiện Đề Xuất

### Bước 1: Chốt baseline và cấu trúc tool

1. Tạo hoặc xác nhận file baseline chatbot ở root, ưu tiên `chatbot.py`.
2. Tạo thư mục `src/tools/` nếu chưa có và định nghĩa các tool tối thiểu.
3. Chạy baseline để có một điểm so sánh trước khi làm agent.

### Bước 2: Hoàn thiện ReAct agent

1. Sửa `src/agent/agent.py` để sinh prompt có format rõ ràng.
2. Parse output của LLM để tách `Thought`, `Action`, và `Final Answer`.
3. Map `Action` sang tool thật trong `src/tools/`.
4. Đẩy `Observation` trở lại prompt cho vòng tiếp theo.
5. Dừng đúng khi có `Final Answer` hoặc chạm `max_steps`.

### Bước 3: Chuẩn hoá provider

1. Kiểm tra `src/core/openai_provider.py`.
2. Kiểm tra `src/core/gemini_provider.py`.
3. Kiểm tra `src/core/local_provider.py` với model GGUF.
4. Đảm bảo cả ba provider trả về cùng cấu trúc dữ liệu để agent không cần biết backend.

### Bước 4: Gắn telemetry và debug

1. Mở rộng logging trong `src/telemetry/logger.py` nếu cần thêm event cho step, tool call, lỗi parse, và lỗi tool.
2. Dùng log để phân tích lý do fail: hallucination, parse error, loop vô hạn, timeout.
3. Ghi lại kết quả chạy để đưa vào report.

### Bước 5: Viết test

1. Giữ hoặc mở rộng `tests/test_local.py` để xác nhận local provider chạy được.
2. Thêm test cho agent để kiểm tra dừng đúng, gọi tool đúng, và xử lý output sai format.
3. Nếu có thể, thêm test cho từng provider để tránh lệch format đầu ra.

### Bước 6: Hoàn thiện báo cáo

1. Điền `report/group_report/TEMPLATE_GROUP_REPORT.md` và lưu thành report cuối cùng theo tên nhóm.
2. Điền `report/individual_reports/TEMPLATE_INDIVIDUAL_REPORT.md` và lưu thành report cá nhân theo tên sinh viên.
3. Trong report, phải có bằng chứng về trace thất bại, phân tích nguyên nhân, và so sánh chatbot vs agent.

## 4. Tiêu Chí Kiểm Tra Hoàn Thành

- Agent chạy được ít nhất một vòng ReAct hoàn chỉnh.
- Có log đủ để xem từng bước reasoning và observation.
- Có baseline chatbot để so sánh với agent.
- Provider local chạy được nếu có model GGUF hợp lệ.
- Report nhóm và cá nhân bám đúng rubric trong `SCORING.md`.

## 5. Lưu Ý Theo Rubric

- `SCORING.md` yêu cầu group report phải có: baseline chatbot, agent v1, agent v2, tiến hoá tool design, trace thành công và thất bại, phân tích dữ liệu, flowchart, và insight.
- `SCORING.md` yêu cầu individual report phải có: đóng góp kỹ thuật, một case study debug, phản tư cá nhân, và ý tưởng mở rộng.
- `EVALUATION.md` nhấn mạnh các metric cần theo dõi là token count, latency, loop count, và failure codes.

## 6. Gợi Ý Ưu Tiên Làm Trước

1. `src/agent/agent.py`
2. `src/tools/`
3. `chatbot.py`
4. `src/telemetry/logger.py`
5. `tests/`
6. `report/group_report/`
7. `report/individual_reports/`

## 7. Ghi Chú Ngắn

Nếu bạn muốn, file này có thể được dùng như checklist làm việc hoặc làm nền để mình tiếp tục sửa code thật trong repo.