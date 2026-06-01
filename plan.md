# Plan MVP 2-3h: Chatbot vs ReAct Agent cho AI Travel Concierge

## 1. Mục tiêu

Xây dựng demo đúng trọng tâm Lab 3: so sánh chatbot baseline với ReAct Agent có tool use, log trace, đo latency/token/cost và phân tích lỗi. Use case chọn là **AI Travel Concierge cho Vinpearl/VinWonders**, nhưng chỉ triển khai đủ cho bài lab trong 2-3 giờ, không làm hệ thống production đầy đủ.

Runtime chính dùng API gateway local đã cấp:

```text
Base URL: http://localhost:20128/v1
Model nhanh: xmtp/mimo-v2.5
Model tốt hơn: xmtp/mimo-v2.5-pro
```

API key đọc từ `.env`, không hardcode vào code, không in key ra log.

## 2. Phạm vi MVP

Làm:

- Chatbot baseline trả lời trực tiếp bằng LLM, không gọi tool.
- ReAct Agent chạy vòng `Thought -> Action -> Observation -> Final Answer`.
- 3 tool mock cho du lịch Vinpearl/VinWonders: `hotel_lookup`, `ticket_offer_lookup`, `itinerary_planner`.
- Provider OpenAI-compatible trỏ tới `http://localhost:20128/v1`.
- CLI demo đổi được model `xmtp/mimo-v2.5` và `xmtp/mimo-v2.5-pro`.
- JSON logs cho LLM call, tool call, loop count, latency, token usage, lỗi.
- Group report có successful trace, failed trace, so sánh chatbot vs agent.

Không làm trong MVP:

- PostgreSQL, Vector DB, crawler, RAG thật.
- Web UI/dashboard.
- Ollama/local model path.
- Google Maps/weather API thật.
- Booking/payment thật.

## 3. Kiến trúc

```text
User query
  -> CLI demo
  -> Chatbot baseline hoặc ReActAgent
  -> OpenAI-compatible API at http://localhost:20128/v1
  -> ReAct parser
  -> Travel tools
  -> Observation
  -> Final Answer
  -> logs/YYYY-MM-DD.log
```

Các module chính:

- `src/core/openai_provider.py`: gọi API theo chuẩn OpenAI, nhận `base_url`.
- `src/core/provider_factory.py`: đọc `.env`, tạo provider với host/key/model.
- `src/agent/agent.py`: ReAct loop, parse action, max steps, final answer.
- `src/tools/travel_tools.py`: mock data có `source_url` và warning.
- `src/demo.py`: chạy demo theo provider/model/query.
- `src/telemetry/logger.py`, `src/telemetry/metrics.py`: ghi log và metric.

## 4. Cấu hình `.env`

Hỗ trợ dạng chuẩn:

```env
OPENAI_BASE_URL=http://localhost:20128/v1
OPENAI_API_KEY=your_api_key
DEFAULT_PROVIDER=openai
DEFAULT_MODEL=xmtp/mimo-v2.5
```

Hoặc dạng `.env` hiện tại:

```text
host: http://localhost:20128/v1
api_key1: your_primary_key
api_key2: your_backup_key
model: xmtp/mimo-v2.5, xmtp/mimo-v2.5-pro
```

Quy tắc model:

- Nếu CLI có `--model`, dùng model đó.
- Nếu không có `--model`, dùng `DEFAULT_MODEL`.
- Nếu `.env` chỉ có dòng `model:` nhiều giá trị, dùng model đầu tiên: `xmtp/mimo-v2.5`.

## 5. Cách gọi model

Chạy model nhanh:

```powershell
python -m src.demo --provider openai --model xmtp/mimo-v2.5
```

Chạy model pro:

```powershell
python -m src.demo --provider openai --model xmtp/mimo-v2.5-pro
```

Chạy theo `.env`:

```powershell
python -m src.demo --provider openai
```

Demo query chính:

```text
Gia đình tôi có 2 người lớn, 2 trẻ em, muốn đi Phú Quốc 3 ngày 2 đêm,
ngân sách khoảng 15 triệu, ưu tiên nghỉ dưỡng và cho trẻ con chơi.
Hãy lập kế hoạch giúp tôi.
```

## 6. Tool MVP

| Tool | Input chính | Output chính |
| --- | --- | --- |
| `hotel_lookup` | `destination`, `group_type`, `budget_vnd`, `nights` | khách sạn gợi ý, giá mock, tiện ích, `source_url`, warning |
| `ticket_offer_lookup` | `destination`, `adults`, `children`, `date` | vé/combo mock, subtotal, `source_url`, warning |
| `itinerary_planner` | `destination`, `days`, `nights`, group, budget, preferences | lịch trình theo ngày, chi phí ước tính, sources, warnings |

Nguyên tắc:

- Giá và lịch trong tool là mock data cho lab, phải ghi rõ cần kiểm tra lại trên nguồn chính thức.
- Agent không được tự bịa giá/vé/lịch nếu tool không trả dữ liệu.
- Nếu tool lỗi, agent phải trả fallback thay vì crash.

## 7. Phân chia nhóm 5 thành viên

| Thành viên | Nhiệm vụ | Đầu ra |
| --- | --- | --- |
| 1 | Agent core | ReAct loop, parser, `max_steps`, unknown tool fallback |
| 2 | Tool/data | 3 travel tools, mock data Phú Quốc/Nha Trang, source URL |
| 3 | Provider/config | API gateway `http://localhost:20128/v1`, đọc `.env`, đổi model qua CLI |
| 4 | Telemetry/evaluation | log token/latency/cost/tool call, test cases, failed trace |
| 5 | Report/demo | group report, flowchart, individual contribution mapping, demo script |

## 8. Timeline 2-3 giờ

| Thời gian | Việc làm |
| --- | --- |
| 0:00-0:20 | Chốt `.env`, model, demo query, phân công nhóm |
| 0:20-1:00 | Implement provider/config và ReAct loop |
| 1:00-1:35 | Implement 3 tools và chatbot baseline |
| 1:35-2:05 | Gắn telemetry/logs và CLI demo |
| 2:05-2:35 | Chạy thử demo, thu trace thành công/thất bại |
| 2:35-3:00 | Điền report nhóm/cá nhân, chuẩn bị trình bày |

## 9. Kịch bản đánh giá

So sánh ít nhất 4 nhóm case:

1. Simple FAQ: hỏi thông tin đơn giản về VinWonders.
2. Multi-step itinerary: Phú Quốc 3 ngày 2 đêm cho gia đình 4 người.
3. Missing information: hỏi lịch trình nhưng thiếu điểm đến/ngân sách.
4. Failure/safety: tool không có dữ liệu, prompt injection, hoặc câu hỏi ngoài phạm vi.

Metrics cần ghi:

- Chatbot vs Agent result.
- Số vòng ReAct.
- Tools đã gọi.
- Latency.
- Token input/output.
- Cost estimate.
- Error type nếu có.

## 10. Tiêu chí hoàn thành

MVP đạt yêu cầu khi:

- Chatbot baseline và ReAct Agent đều chạy được qua API gateway local.
- ReAct Agent gọi ít nhất 2 tool trong case itinerary.
- Final answer có lịch trình, chi phí ước tính, warning mock data và source URL.
- Logs có đủ LLM metric, tool call, loop count và lỗi nếu xảy ra.
- Group report có successful trace, failed trace, so sánh chatbot vs agent và đóng góp từng thành viên.
