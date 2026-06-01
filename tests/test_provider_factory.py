from src.core.provider_factory import _first_model, _normalize_base_url, create_provider_from_env


def test_provider_factory_rejects_unknown_provider():
    try:
        create_provider_from_env(provider="unknown")
    except ValueError as exc:
        assert "Unsupported provider" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_first_model_uses_first_comma_separated_model():
    assert _first_model("xmtp/mimo-v2.5, xmtp/mimo-v2.5-pro") == "xmtp/mimo-v2.5"


def test_normalize_base_url_defaults_to_required_gateway():
    assert _normalize_base_url(None) == "http://localhost:20128/v1"


def test_normalize_base_url_handles_loose_host_note():
    value = "http://localhost:20128/v1 or https://example.invalid/v1"
    assert _normalize_base_url(value) == "http://localhost:20128/v1"
