from typing import Dict, Any, List
from src.telemetry.logger import logger


MODEL_PRICING_USD_PER_1M = {
    # Lab estimate values. Adjust here if the gateway owner provides exact prices.
    "xmtp/mimo-v2.5": {"input": 0.15, "output": 0.60},
    "xmtp/mimo-v2.5-pro": {"input": 0.50, "output": 2.00},
    "default": {"input": 0.25, "output": 1.00},
}


class PerformanceTracker:
    """
    Tracking industry-standard metrics for LLMs.
    """
    def __init__(self):
        self.session_metrics = []

    def track_request(self, provider: str, model: str, usage: Dict[str, int], latency_ms: int):
        """
        Logs a single request metric to our telemetry.
        """
        metric = {
            "provider": provider,
            "model": model,
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0),
            "latency_ms": latency_ms,
            "cost_estimate": self._calculate_cost(model, usage),
            "pricing_unit": "USD_PER_1M_TOKENS",
        }
        self.session_metrics.append(metric)
        logger.log_event("LLM_METRIC", metric)

    def _calculate_cost(self, model: str, usage: Dict[str, int]) -> float:
        """
        Estimate request cost from prompt/completion tokens.
        """
        pricing = MODEL_PRICING_USD_PER_1M.get(model, MODEL_PRICING_USD_PER_1M["default"])
        input_tokens = usage.get("prompt_tokens", 0)
        output_tokens = usage.get("completion_tokens", 0)
        return round(
            (input_tokens / 1_000_000) * pricing["input"]
            + (output_tokens / 1_000_000) * pricing["output"],
            8,
        )

    def snapshot(self) -> int:
        return len(self.session_metrics)

    def since(self, start_index: int) -> List[Dict[str, Any]]:
        return self.session_metrics[start_index:]

    def summary(self) -> Dict[str, Any]:
        if not self.session_metrics:
            return {
                "requests": 0,
                "total_tokens": 0,
                "total_cost_usd": 0.0,
                "avg_latency_ms": 0,
                "max_latency_ms": 0,
            }

        total_latency = sum(metric["latency_ms"] for metric in self.session_metrics)
        return {
            "requests": len(self.session_metrics),
            "total_tokens": sum(metric["total_tokens"] for metric in self.session_metrics),
            "total_cost_usd": round(sum(metric["cost_estimate"] for metric in self.session_metrics), 8),
            "avg_latency_ms": int(total_latency / len(self.session_metrics)),
            "max_latency_ms": max(metric["latency_ms"] for metric in self.session_metrics),
        }

# Global tracker instance
tracker = PerformanceTracker()
