# Lab 3: Chatbot vs ReAct Agent

This repo is a 2-3 hour MVP for comparing a direct chatbot baseline with a
tool-using ReAct agent. The domain demo is a Vinpearl/VinWonders travel
concierge.

## Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure `.env` with the lab API gateway:

```text
host: http://localhost:20128/v1
api_key1: your_primary_key
api_key2: your_backup_key
model: xmtp/mimo-v2.5, xmtp/mimo-v2.5-pro
```

Standard dotenv format is also supported:

```env
OPENAI_BASE_URL=http://localhost:20128/v1
OPENAI_API_KEY=your_key
DEFAULT_PROVIDER=openai
DEFAULT_MODEL=xmtp/mimo-v2.5
```

## Run Demo

Chatbot baseline only:

```bash
python -m src.demo --mode chatbot --provider openai --model xmtp/mimo-v2.5
```

ReAct agent only:

```bash
python -m src.demo --mode agent --provider openai --model xmtp/mimo-v2.5
```

Compare chatbot vs agent:

```bash
python -m src.demo --mode compare --provider openai --model xmtp/mimo-v2.5-pro
```

Run the browser UI:

```bash
python -m src.web_server --host 127.0.0.1 --port 8000
```

Then open `http://127.0.0.1:8000/`.

Run the Streamlit chat UI:

```bash
streamlit run streamlit_app.py --server.address 127.0.0.1 --server.port 8501
```

Then open `http://127.0.0.1:8501/`.

The Streamlit UI shows the lab metrics required for evaluation:

- LLM call count
- input/output/total tokens
- estimated request cost
- average/max latency
- request metric table
- raw JSON log tail from `logs/YYYY-MM-DD.log`
- session history context used for follow-up questions

If `--model` is omitted, the app uses `DEFAULT_MODEL`; if that is missing, it
uses the first model listed in the `.env` `model:` line.

## What The MVP Includes

- `src/chatbot.py`: direct LLM baseline with no tools.
- `src/agent/agent.py`: ReAct loop with `Thought -> Action -> Observation`.
- `src/tools/travel_tools.py`: mock travel tools with source URLs and warnings.
- `src/core/provider_factory.py`: config loader for `.env` and the gateway.
- `src/telemetry/`: JSON logs for metrics, tool calls, and errors.

## Evaluation Focus

Use `logs/YYYY-MM-DD.log` to compare:

- chatbot vs agent result quality
- loop count
- tools called
- token usage
- latency
- estimated cost
- parser/tool/provider errors
